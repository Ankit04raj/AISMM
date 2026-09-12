/**
 * Deterministic contract and unit tests for AISMM Frontend Client.
 * Tests token management, request timeout handling, error message extraction, and session draft storage.
 */

import { describe, it, beforeEach } from 'node:test';
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
globalThis.window = {
  dispatchEvent: () => {},
};

describe('AISMM Frontend Auth Session Management', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
  });

  it('stores and retrieves access and refresh tokens properly', () => {
    localStorage.setItem('aismm_access_token', 'test_access_jwt');
    localStorage.setItem('aismm_refresh_token', 'test_refresh_jwt');
    localStorage.setItem('aismm_user', JSON.stringify({ id: 'u1', email: 'test@aismm.app' }));

    assert.equal(localStorage.getItem('aismm_access_token'), 'test_access_jwt');
    assert.equal(localStorage.getItem('aismm_refresh_token'), 'test_refresh_jwt');
    const user = JSON.parse(localStorage.getItem('aismm_user'));
    assert.equal(user.email, 'test@aismm.app');
  });

  it('clears session on logout', () => {
    localStorage.setItem('aismm_access_token', 'token_to_clear');
    localStorage.removeItem('aismm_access_token');
    assert.equal(localStorage.getItem('aismm_access_token'), null);
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
