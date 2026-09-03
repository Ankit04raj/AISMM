/**
 * AISMM Centralized API Client
 * Connects React UI to FastAPI Backend v1 endpoints with JWT Authorization headers.
 * Never silently masks offline/failed states with fake numbers.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

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

export async function fetchApi(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({ detail: res.statusText }));
      const errorMsg = errorBody.detail || errorBody.message || `HTTP ${res.status} Error`;
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err) {
    console.error(`[AISMM API Error] ${endpoint}:`, err.message);
    throw err;
  }
}

export const api = {
  // Authentication & Session
  login: (email, password) => fetchApi("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (email, password, full_name) => fetchApi("/auth/register", { method: "POST", body: JSON.stringify({ email, password, full_name }) }),
  getMe: () => fetchApi("/auth/me"),
  refreshToken: (refresh_token) => fetchApi("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token }) }),

  // Health & System
  getLiveness: () => fetchApi("/health/liveness"),
  getReadiness: () => fetchApi("/health/readiness"),
  getTelemetry: () => fetchApi("/health/telemetry"),

  // Accounts & Platforms
  getAccounts: () => fetchApi("/accounts"),
  getAccount: (id) => fetchApi(`/accounts/${id}`),
  connectAccount: (data) => fetchApi("/accounts/connect", { method: "POST", body: JSON.stringify(data) }),
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
