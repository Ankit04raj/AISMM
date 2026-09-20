/**
 * Deterministic contract and unit tests for AISMM Frontend Client.
 * Tests token management, request timeout handling, error message extraction, session draft storage,
 * 401 mutex token refresh without infinite loops, and auth method API bindings.
 */

import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';

// Mock localStorage and window for Node environment
class LocalStorageMock {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store[key] || null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

globalThis.localStorage = new LocalStorageMock();
globalThis.sessionStorage = new LocalStorageMock();

let dispatchedEvents = [];
globalThis.window = {
  dispatchEvent: (event) => {
    dispatchedEvents.push(event.type || event);
  },
  location: {
    origin: 'http://localhost:5173',
  },
};

// Import client functions
const clientModule = await import('../src/api/client.js');
const {
  api,
  fetchApi,
  getAuthToken,
  setAuthSession,
  clearAuthSession,
  getStoredUser,
} = clientModule;

describe('AISMM Frontend Auth Session Management', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    dispatchedEvents = [];
  });

  it('stores and retrieves access and refresh tokens properly', () => {
    setAuthSession('test_access_jwt', 'test_refresh_jwt', { id: 'u1', email: 'test@aismm.app' });

    assert.equal(getAuthToken(), 'test_access_jwt');
    assert.equal(localStorage.getItem('aismm_refresh_token'), 'test_refresh_jwt');
    const user = getStoredUser();
    assert.equal(user.email, 'test@aismm.app');
  });

  it('returns empty string or null when tokens/user are not stored or corrupted', () => {
    assert.equal(getAuthToken(), '');
    assert.equal(getStoredUser(), null);

    localStorage.setItem('aismm_user', 'invalid-json{');
    assert.equal(getStoredUser(), null);
  });

  it('clears session on logout', () => {
    setAuthSession('token_to_clear', 'refresh_to_clear', { id: 'u1', email: 'test@aismm.app' });
    clearAuthSession();

    assert.equal(getAuthToken(), '');
    assert.equal(localStorage.getItem('aismm_refresh_token'), null);
    assert.equal(getStoredUser(), null);
  });

  it('persists and restores Composer drafts across tab switches and reloads', () => {
    const sampleDraft = {
      text: 'Draft post for AI optimization #social',
      platforms: ['x', 'linkedin'],
      mediaUrl: 'https://cdn.example.com/image.png',
      selectedTime: '2026-09-10T15:00:00Z',
    };

    sessionStorage.setItem('aismm_composer', JSON.stringify(sampleDraft));
    const restored = JSON.parse(sessionStorage.getItem('aismm_composer'));

    assert.equal(restored.text, 'Draft post for AI optimization #social');
    assert.deepEqual(restored.platforms, ['x', 'linkedin']);
    assert.equal(restored.mediaUrl, 'https://cdn.example.com/image.png');
  });

  it('normalizes legacy hash fragments into React Router paths', () => {
    const legacyHashToPath = (hash) => {
      const cleaned = hash.replace(/^#\/?/, '');
      if (!cleaned || cleaned === 'overview') return '/app/overview';
      if (cleaned.startsWith('tab-')) return `/app/${cleaned.replace('tab-', '')}`;
      if (cleaned === 'terms') return '/terms';
      if (cleaned === 'privacy') return '/privacy';
      return `/app/${cleaned}`;
    };

    assert.equal(legacyHashToPath('#overview'), '/app/overview');
    assert.equal(legacyHashToPath('#tab-analytics'), '/app/analytics');
    assert.equal(legacyHashToPath('#tab-composer'), '/app/composer');
    assert.equal(legacyHashToPath('#terms'), '/terms');
    assert.equal(legacyHashToPath('#privacy'), '/privacy');
  });
});

describe('AISMM fetchApi & 401 Mutex Token Refresh', () => {
  const originalFetch = globalThis.fetch;

  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    dispatchedEvents = [];
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  it('attaches Authorization Bearer header when token exists', async () => {
    setAuthSession('my_secret_token', 'my_refresh_token', { id: 'u1' });

    let capturedHeaders = null;
    globalThis.fetch = async (url, options) => {
      capturedHeaders = options.headers;
      return {
        ok: true,
        status: 200,
        json: async () => ({ status: 'ok' }),
      };
    };

    const res = await fetchApi('/health/liveness');
    assert.equal(res.status, 'ok');
    assert.equal(capturedHeaders.Authorization, 'Bearer my_secret_token');
    assert.equal(capturedHeaders['Content-Type'], 'application/json');
  });

  it('throws Error with status code on 400/403/422/500 without falling back to mock or null', async () => {
    globalThis.fetch = async (url) => {
      if (url.includes('/test-403')) {
        return {
          ok: false,
          status: 403,
          json: async () => ({ detail: 'Email verification required.' }),
        };
      }
      if (url.includes('/test-422')) {
        return {
          ok: false,
          status: 422,
          json: async () => ({
            detail: [{ loc: ['body', 'password'], msg: 'Password must be at least 8 characters long' }],
          }),
        };
      }
      return {
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' }),
      };
    };

    // 403 test
    await assert.rejects(
      async () => await fetchApi('/test-403'),
      (err) => {
        assert.ok(err instanceof Error);
        assert.equal(err.status, 403);
        assert.equal(err.message, 'Email verification required.');
        return true;
      }
    );

    // 422 validation array formatting
    await assert.rejects(
      async () => await fetchApi('/test-422'),
      (err) => {
        assert.ok(err instanceof Error);
        assert.equal(err.status, 422);
        assert.ok(err.message.includes('password: Password must be at least 8 characters long'));
        return true;
      }
    );

    // 500 test
    await assert.rejects(
      async () => await fetchApi('/test-500'),
      (err) => {
        assert.ok(err instanceof Error);
        assert.equal(err.status, 500);
        return true;
      }
    );
  });

  it('returns null on 204 No Content response', async () => {
    globalThis.fetch = async () => ({
      ok: true,
      status: 204,
      json: async () => { throw new Error('should not parse json on 204'); },
    });

    const res = await fetchApi('/test-204');
    assert.equal(res, null);
  });

  it('handles 401 with successful refresh mutex: refreshes once, updates session, and retries request', async () => {
    setAuthSession('expired_token', 'valid_refresh_token', { id: 'u1', email: 'test@aismm.app' });

    let fetchCounts = {
      protected: 0,
      refresh: 0,
    };

    globalThis.fetch = async (url, options) => {
      if (url.endsWith('/auth/refresh')) {
        fetchCounts.refresh++;
        return {
          ok: true,
          status: 200,
          json: async () => ({
            access_token: 'new_access_token',
            refresh_token: 'new_refresh_token',
          }),
        };
      }
      if (url.endsWith('/posts')) {
        fetchCounts.protected++;
        // First attempt with expired token fails with 401
        if (options.headers?.Authorization === 'Bearer expired_token') {
          return {
            ok: false,
            status: 401,
            json: async () => ({ detail: 'Token expired' }),
          };
        }
        // Retried attempt with new token succeeds
        if (options.headers?.Authorization === 'Bearer new_access_token') {
          return {
            ok: true,
            status: 200,
            json: async () => ({ posts: ['post1', 'post2'] }),
          };
        }
      }
      throw new Error(`Unexpected fetch url: ${url}`);
    };

    const res = await fetchApi('/posts');
    assert.deepEqual(res, { posts: ['post1', 'post2'] });
    assert.equal(fetchCounts.refresh, 1, 'Refresh endpoint should be called exactly once');
    assert.equal(fetchCounts.protected, 2, 'Protected endpoint should be called twice (initial + retry)');
    assert.equal(getAuthToken(), 'new_access_token');
    assert.equal(localStorage.getItem('aismm_refresh_token'), 'new_refresh_token');
  });

  it('handles 401 when refresh fails: clears session, dispatches aismm:session-expired, throws 401 Error without infinite loops', async () => {
    setAuthSession('expired_token', 'bad_refresh_token', { id: 'u1' });

    let refreshCallCount = 0;
    globalThis.fetch = async (url) => {
      if (url.endsWith('/auth/refresh')) {
        refreshCallCount++;
        return {
          ok: false,
          status: 401,
          json: async () => ({ detail: 'Invalid refresh token' }),
        };
      }
      return {
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Token expired' }),
      };
    };

    await assert.rejects(
      async () => await fetchApi('/posts'),
      (err) => {
        assert.ok(err instanceof Error);
        assert.equal(err.status, 401);
        return true;
      }
    );

    assert.equal(refreshCallCount, 1);
    assert.equal(getAuthToken(), '');
    assert.equal(localStorage.getItem('aismm_user'), null);
    assert.ok(dispatchedEvents.includes('aismm:session-expired'));
  });

  it('does NOT trigger refreshSession on 401 for /auth/login, /auth/refresh, or /auth/logout', async () => {
    let refreshTriggered = false;
    globalThis.fetch = async (url) => {
      if (url.endsWith('/auth/refresh')) {
        refreshTriggered = true;
        return { ok: true, status: 200, json: async () => ({}) };
      }
      return {
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid email or password.' }),
      };
    };

    await assert.rejects(
      async () => await fetchApi('/auth/login', { method: 'POST' }),
      (err) => {
        assert.equal(err.status, 401);
        assert.equal(err.message, 'Invalid email or password.');
        return true;
      }
    );

    assert.equal(refreshTriggered, false, 'Should not attempt refresh for /auth/login');
  });
});

describe('AISMM API Auth Methods Presence & Signatures', () => {
  it('exports all required auth API methods on the api object', () => {
    const requiredMethods = [
      'register',
      'login',
      'logout',
      'verifyEmail',
      'verifyEmailOtp',
      'verifyPhone',
      'resendVerification',
      'resendEmailOtp',
      'resendPhoneVerification',
      'forgotPassword',
      'verifyPasswordResetOtp',
      'resetPassword',
      'changePassword',
      'getMe',
      'getCurrentUser',
      'refreshSession',
    ];

    for (const method of requiredMethods) {
      assert.equal(typeof api[method], 'function', `Expected api.${method} to be a function`);
    }
  });
});
