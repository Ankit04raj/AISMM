/**
 * AISMM Centralized API Client
 * Connects React UI to FastAPI Backend v1 endpoints with JWT Authorization headers.
 * Never silently masks offline/failed states with fake numbers.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

// Auth Token Management in Browser LocalStorage
export function getAuthToken() {
  return localStorage.getItem("aismm_access_token") || "";
}

export function setAuthSession(accessToken, refreshToken, user) {
  if (accessToken) localStorage.setItem("aismm_access_token", accessToken);
  if (refreshToken) localStorage.setItem("aismm_refresh_token", refreshToken);
  if (user) localStorage.setItem("aismm_user", JSON.stringify(user));
}

export function clearAuthSession() {
  localStorage.removeItem("aismm_access_token");
  localStorage.removeItem("aismm_refresh_token");
  localStorage.removeItem("aismm_user");
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem("aismm_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

let refreshInFlight = null;
async function refreshSession() {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const refresh_token = localStorage.getItem('aismm_refresh_token');
      if (!refresh_token) return false;
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token }), signal: AbortSignal.timeout(15000),
      });
      if (!response.ok) return false;
      const data = await response.json();
      setAuthSession(data.access_token, data.refresh_token);
      return true;
    })().finally(() => { refreshInFlight = null; });
  }
  return refreshInFlight;
}

export async function fetchApi(endpoint, options = {}, retry = true) {
  const token = getAuthToken();
  let res;
  try {
    res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      signal: options.signal || AbortSignal.timeout(45000),
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
    });
  } catch (error) {
    throw new Error(error.name === 'TimeoutError' ? 'The server took too long to respond. Please retry.' : 'Unable to reach AISMM backend. Check your connection.');
  }
  if (res.status === 401 && token && retry && !['/auth/login', '/auth/refresh', '/auth/logout'].includes(endpoint)) {
    if (await refreshSession().catch(() => false)) return fetchApi(endpoint, options, false);
    clearAuthSession();
    window.dispatchEvent(new Event('aismm:session-expired'));
  }
  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail || data?.message;
    const message = Array.isArray(detail) ? detail.map(item => `${item.loc?.slice(-1)[0] || 'Input'}: ${item.msg}`).join('; ')
      : typeof detail === 'string' ? detail : `Request failed (${res.status}). Please retry.`;
    const error = new Error(message); error.status = res.status; throw error;
  }
  return data;
}

export const api = {
  getInbox: () => fetchApi('/comments'),
  syncInbox: () => fetchApi('/comments/sync', {method:'POST'}),
  logout: () => fetchApi('/auth/logout', { method: 'POST', body: JSON.stringify({ refresh_token: localStorage.getItem('aismm_refresh_token') }) }),
  updateProfile: (full_name) => fetchApi('/auth/me', { method: 'PATCH', body: JSON.stringify({ full_name }) }),
  changePassword: (data) => fetchApi('/auth/password', { method: 'POST', body: JSON.stringify(data) }),
  setup2fa: () => fetchApi('/auth/2fa/setup', { method: 'POST' }),
  enable2fa: (code) => fetchApi('/auth/2fa/enable', { method: 'POST', body: JSON.stringify({ code }) }),
  disable2fa: (code) => fetchApi('/auth/2fa/disable', { method: 'POST', body: JSON.stringify({ code }) }),
  forgotPassword: (email) => fetchApi('/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
  resetPassword: (token, password) => fetchApi('/auth/reset-password', { method: 'POST', body: JSON.stringify({ token, password }) }),
  initOAuth: (platform) => fetchApi('/auth/oauth/init', { method: 'POST', body: JSON.stringify({ platform, redirect_uri: `${window.location.origin}/oauth/callback` }) }),
  completeOAuth: (data) => fetchApi('/auth/oauth/callback', { method: 'POST', body: JSON.stringify(data) }),

  // Authentication & Session
  login: (email, password, two_factor_code) => fetchApi("/auth/login", { method: "POST", body: JSON.stringify({ email, password, two_factor_code }) }),
  register: (email, password, full_name, phone_number, verification_method) => fetchApi("/auth/register", { method: "POST", body: JSON.stringify({ email, password, full_name, phone_number: phone_number || null, verification_method, accept_terms: true }) }),
  verifyEmail: (code) => fetchApi("/auth/verify-email", { method: "POST", body: JSON.stringify({ code }) }),
  verifyPhone: (code, phone_number) => fetchApi("/auth/verify-phone", { method: "POST", body: JSON.stringify({ code, phone_number }) }),
  resendVerification: () => fetchApi("/auth/resend-verification", { method: "POST" }),
  resendPhoneVerification: () => fetchApi("/auth/resend-phone-verification", { method: "POST" }),
  getMe: () => fetchApi("/auth/me"),
  refreshToken: (refresh_token) => fetchApi("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token }) }),

  // Health & System
  getLiveness: () => fetchApi("/health/liveness"),
  getReadiness: () => fetchApi("/health/readiness"),
  getTelemetry: () => fetchApi("/health/telemetry"),

  // Accounts & Platforms
  getAccounts: () => fetchApi("/accounts"),
  getAccount: (id) => fetchApi(`/accounts/${id}`),
  getAccountProfile: (id) => fetchApi(`/accounts/${id}/profile`),
  syncAccount: (id) => fetchApi(`/accounts/${id}/sync`, { method: "POST" }),
  connectAccount: (data) => fetchApi("/accounts/connect", { method: "POST", body: JSON.stringify(data) }),
  directConnectAccount: (data) => fetchApi("/accounts/direct-connect", { method: "POST", body: JSON.stringify(data) }),
  disconnectAccount: (id) => fetchApi(`/accounts/${id}`, { method: "DELETE" }),
  listPlatforms: () => fetchApi("/platforms"),
  getPlatformCapabilities: (platform) => fetchApi(`/platforms/${platform}/capabilities`),

  // Posts & Content Management
  getPosts: (page = 1, pageSize = 20, platform = null, statusFilter = null) => {
    let url = `/posts?page=${page}&page_size=${pageSize}`;
    if (platform) url += `&platform=${platform}`;
    if (statusFilter) url += `&status_filter=${statusFilter}`;
    return fetchApi(url);
  },
  createPost: (data) => fetchApi("/posts", { method: "POST", body: JSON.stringify(data) }),
  deletePost: (id) => fetchApi(`/posts/${id}`, { method: "DELETE" }),
  previewContent: (data) => fetchApi("/content/preview", { method: "POST", body: JSON.stringify(data) }),
  validateContent: (data) => fetchApi("/content/validate", { method: "POST", body: JSON.stringify(data) }),
  publishMultiPlatform: (data) => fetchApi("/content/publish-multi", { method: "POST", body: JSON.stringify(data) }),
  retryPublication: (postId, platform) => fetchApi(`/content/${postId}/retry/${platform}`, { method: "POST" }),

  // Universal Analytics Dashboard
  getOverview: (days = 30) => fetchApi(`/analytics/dashboard?days=${days}`),
  getPlatformComparison: (days = 30) => fetchApi(`/analytics/comparison?days=${days}`),
  getContentPerformance: (days = 30) => fetchApi(`/analytics/content?days=${days}`),
  getTemporalHeatmap: (days = 30) => fetchApi(`/analytics/temporal?days=${days}`),
  getSentimentTrends: (days = 30) => fetchApi(`/analytics/sentiment-trends?days=${days}`),
  getGrowthAccuracy: (platform = "instagram") => fetchApi(`/analytics/growth-accuracy?platform=${platform}`),

  // Strategy & Recommendations
  getStrategyDashboard: () => fetchApi("/strategy/dashboard"),
  generateContentPlan: (data) => fetchApi("/strategy/content-plan", { method: "POST", body: JSON.stringify(data) }),
  getPlatformAdvice: (platform) => fetchApi(`/strategy/platform-advice/${platform}`),
  submitStrategyFeedback: (data) => fetchApi("/strategy/feedback", { method: "POST", body: JSON.stringify(data) }),

  // Intelligent Scheduling
  recommendTimes: (data) => fetchApi("/scheduling/recommend-times", { method: "POST", body: JSON.stringify(data) }),
  autoSchedule: (data) => fetchApi("/scheduling/auto-schedule", { method: "POST", body: JSON.stringify(data) }),
  triggerDuePosts: () => fetchApi("/scheduling/trigger-due", { method: "POST" }),

  // AI Content Tools
  analyzeSentiment: (text) => fetchApi("/ai/sentiment/analyze", { method: "POST", body: JSON.stringify({ text }) }),
  analyzePostCommentsSentiment: (comments) => fetchApi("/ai/sentiment/comments", { method: "POST", body: JSON.stringify({ comments }) }),
  analyzeCaption: (text, platform) => fetchApi("/ai/caption/analyze", { method: "POST", body: JSON.stringify({ text, platform }) }),
  optimizeCaption: (text, platform, tone) => fetchApi("/ai/caption/optimize", { method: "POST", body: JSON.stringify({ text, platform, target_tone: tone }) }),
  recommendHashtags: (text, platform, topK = 5) => fetchApi("/ai/hashtags/recommend", { method: "POST", body: JSON.stringify({ text, platform, top_k: topK }) }),
  optimizeContentAll: (data) => fetchApi("/ai/content/optimize-all", { method: "POST", body: JSON.stringify(data) }),

  // Post Intelligence
  syncPostComments: (postId, limit = 50) => fetchApi(`/intelligence/posts/${postId}/sync-comments`, { method: "POST", body: JSON.stringify({ limit_per_platform: limit }) }),
  getPostSentimentTrajectory: (postId) => fetchApi(`/intelligence/posts/${postId}/sentiment-trajectory`),
  getPostAlerts: (postId) => fetchApi(`/intelligence/posts/${postId}/alerts`),
  getPostIntelligenceReport: (postId) => fetchApi(`/intelligence/posts/${postId}/report`),

  // Auto-Reply & Inbox
  classifyComment: (text) => fetchApi("/reply/classify", { method: "POST", body: JSON.stringify({ text }) }),
  suggestReply: (commentText, commentId = "", automationMode = "automatic") => fetchApi("/reply/suggest", { method: "POST", body: JSON.stringify({ comment_text: commentText, comment_id: commentId, automation_mode: automationMode }) }),
  approveReply: (data) => fetchApi("/reply/approve", { method: "POST", body: JSON.stringify(data) }),
  listComments: (platform, postId) => fetchApi(`/comments/posts/${platform}/${postId}`),
  replyComment: (platform, commentId, text) => fetchApi(`/comments/${platform}/${commentId}/reply`, { method: "POST", body: JSON.stringify({ text }) }),
  deleteComment: (platform, commentId) => fetchApi(`/comments/${platform}/${commentId}`, { method: "DELETE" }),
  hideComment: (platform, commentId) => fetchApi(`/comments/${platform}/${commentId}/hide`, { method: "POST" }),

  // Growth Predictions
  predictGrowth: (data) => fetchApi("/growth/predict", { method: "POST", body: JSON.stringify(data) }),
  getAccountGrowthProjections: (accountId) => fetchApi(`/growth/accounts/${accountId}/projections`),
  getGrowthModelsStatus: () => fetchApi("/growth/models/status"),

  // Models & Registry
  getModelRegistry: () => fetchApi("/models/registry"),
  evaluateAllModels: () => fetchApi("/models/evaluate-all"),
  evaluateSingleModel: (name) => fetchApi(`/models/${name}/evaluation`),
  getModelFeatureImportance: (name) => fetchApi(`/models/${name}/feature-importance`),
  checkModelDrift: (name, metric) => fetchApi(`/models/${name}/drift?current_metric=${metric}`),
  promoteModel: (name, targetStage, reason) => fetchApi(`/models/${name}/promote`, { method: "POST", body: JSON.stringify({ target_stage: targetStage, reason }) }),
};
