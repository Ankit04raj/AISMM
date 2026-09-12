/**
 * AISMM Multi-Platform Social OAuth Configuration & Redirect Matrix (JavaScript)
 * Supports dynamic local development and production environment domains.
 */

export function getBaseAppUrl() {
  if (typeof window !== 'undefined' && window.location && window.location.origin) {
    return window.location.origin;
  }
  return (typeof process !== 'undefined' && (process.env?.VITE_APP_URL || process.env?.FRONTEND_URL)) || 'http://localhost:3000';
}

export function getRedirectUri(provider) {
  const base = getBaseAppUrl().replace(/\/+$/, '');
  const config = SOCIAL_OAUTH_CONFIG[provider];
  if (!config) {
    throw new Error(`Unsupported OAuth provider: ${provider}`);
  }
  return `${base}${config.callbackPath}`;
}

export const SOCIAL_OAUTH_CONFIG = {
  meta: {
    name: 'Meta',
    provider: 'meta',
    displayName: 'Meta (Facebook & Instagram)',
    authorizationUrl: 'https://www.facebook.com/v20.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v20.0/oauth/access_token',
    defaultScopes: [
      'pages_show_list',
      'pages_read_engagement',
      'pages_manage_posts',
      'instagram_basic',
      'instagram_content_publish',
      'instagram_manage_insights',
    ],
    callbackPath: '/api/auth/meta/callback',
    developerPortalUrl: 'https://developers.facebook.com/apps',
    documentationUrl: 'https://developers.facebook.com/docs/facebook-login',
    pkceRequired: false,
    responseType: 'code',
  },
  facebook: {
    name: 'Facebook',
    provider: 'facebook',
    displayName: 'Facebook Pages',
    authorizationUrl: 'https://www.facebook.com/v20.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v20.0/oauth/access_token',
    defaultScopes: [
      'pages_show_list',
      'pages_read_engagement',
      'pages_manage_posts',
      'read_insights',
    ],
    callbackPath: '/api/auth/meta/callback',
    developerPortalUrl: 'https://developers.facebook.com/apps',
    documentationUrl: 'https://developers.facebook.com/docs/pages',
    pkceRequired: false,
    responseType: 'code',
  },
  instagram: {
    name: 'Instagram',
    provider: 'instagram',
    displayName: 'Instagram Business',
    authorizationUrl: 'https://www.facebook.com/v20.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v20.0/oauth/access_token',
    defaultScopes: [
      'instagram_basic',
      'instagram_content_publish',
      'instagram_manage_insights',
      'pages_show_list',
      'pages_read_engagement',
    ],
    callbackPath: '/api/auth/meta/callback',
    developerPortalUrl: 'https://developers.facebook.com/apps',
    documentationUrl: 'https://developers.facebook.com/docs/instagram-api',
    pkceRequired: false,
    responseType: 'code',
  },
  x: {
    name: 'X',
    provider: 'x',
    displayName: 'X (Twitter v2)',
    authorizationUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    defaultScopes: [
      'tweet.read',
      'tweet.write',
      'users.read',
      'offline.access',
    ],
    callbackPath: '/api/auth/twitter/callback',
    developerPortalUrl: 'https://developer.twitter.com/en/portal/dashboard',
    documentationUrl: 'https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code',
    pkceRequired: true,
    responseType: 'code',
  },
  twitter: {
    name: 'Twitter',
    provider: 'twitter',
    displayName: 'X (Twitter v2)',
    authorizationUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    defaultScopes: [
      'tweet.read',
      'tweet.write',
      'users.read',
      'offline.access',
    ],
    callbackPath: '/api/auth/twitter/callback',
    developerPortalUrl: 'https://developer.twitter.com/en/portal/dashboard',
    documentationUrl: 'https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code',
    pkceRequired: true,
    responseType: 'code',
  },
  linkedin: {
    name: 'LinkedIn',
    provider: 'linkedin',
    displayName: 'LinkedIn',
    authorizationUrl: 'https://www.linkedin.com/oauth/v2/authorization',
    tokenUrl: 'https://www.linkedin.com/oauth/v2/accessToken',
    defaultScopes: [
      'openid',
      'profile',
      'email',
      'w_member_social',
      'r_organization_social',
      'w_organization_social',
    ],
    callbackPath: '/api/auth/linkedin/callback',
    developerPortalUrl: 'https://www.linkedin.com/developers/apps',
    documentationUrl: 'https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow',
    pkceRequired: false,
    responseType: 'code',
  },
  google: {
    name: 'Google',
    provider: 'google',
    displayName: 'Google / YouTube',
    authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    defaultScopes: [
      'https://www.googleapis.com/auth/userinfo.profile',
      'https://www.googleapis.com/auth/youtube.readonly',
      'https://www.googleapis.com/auth/youtube.upload',
    ],
    callbackPath: '/api/auth/google/callback',
    developerPortalUrl: 'https://console.cloud.google.com/apis/credentials',
    documentationUrl: 'https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps',
    pkceRequired: false,
    responseType: 'code',
  },
  youtube: {
    name: 'YouTube',
    provider: 'youtube',
    displayName: 'YouTube',
    authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    defaultScopes: [
      'https://www.googleapis.com/auth/userinfo.profile',
      'https://www.googleapis.com/auth/youtube.readonly',
      'https://www.googleapis.com/auth/youtube.upload',
    ],
    callbackPath: '/api/auth/google/callback',
    developerPortalUrl: 'https://console.cloud.google.com/apis/credentials',
    documentationUrl: 'https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps',
    pkceRequired: false,
    responseType: 'code',
  },
};
