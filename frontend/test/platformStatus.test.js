import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  labelForConnectionStatus,
  normalizeConnectionStatus,
  selectAccountForPlatform,
  shouldOfferReconnect,
} from '../src/platformStatus.js';

describe('platform connection status presentation', () => {
  it('maps the three server statuses to exact labels', () => {
    assert.equal(labelForConnectionStatus('connected_live'), 'Connected (Live)');
    assert.equal(labelForConnectionStatus('token_expired'), 'Token Expired');
    assert.equal(labelForConnectionStatus('disconnected'), 'Disconnected');
  });

  it('treats missing or unknown status as Disconnected', () => {
    assert.equal(normalizeConnectionStatus(undefined), 'disconnected');
    assert.equal(normalizeConnectionStatus('oauth'), 'disconnected');
    assert.equal(labelForConnectionStatus(null), 'Disconnected');
  });

  it('offers reconnect for expired and unverified rows, not live rows', () => {
    assert.equal(shouldOfferReconnect('token_expired'), true);
    assert.equal(shouldOfferReconnect('disconnected'), true);
    assert.equal(shouldOfferReconnect('connected_live'), false);
    assert.equal(shouldOfferReconnect('mystery'), true);
  });

  it('selects a live account over an earlier seeded disconnected row on the same platform', () => {
    const selected = selectAccountForPlatform([
      { id: 'seed', platform: 'x', connection_status: 'disconnected' },
      { id: 'live', platform: 'x', connection_status: 'connected_live' },
      { id: 'other', platform: 'instagram', connection_status: 'connected_live' },
    ], 'x');
    assert.equal(selected.id, 'live');
  });

  it('prefers expired over disconnected when no live row exists', () => {
    const selected = selectAccountForPlatform([
      { id: 'demo', platform: 'instagram', connection_status: 'disconnected' },
      { id: 'expired', platform: 'instagram', connection_status: 'token_expired' },
    ], 'instagram');
    assert.equal(selected.id, 'expired');
  });
});
