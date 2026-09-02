/**
 * AISMM API Client - Connects React UI to FastAPI Backend v1 endpoints
 * with graceful fallback simulation if backend is offline.
 */

const API_BASE = "http://localhost:8000/api/v1";

export async function fetchApi(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      throw new Error(`API Error: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.warn(`[AISMM API] Using fallback/mock for ${endpoint}:`, err.message);
    return null;
  }
}

export const api = {
  // Health & System
  getLiveness: () => fetchApi("/health/liveness"),
  getReadiness: () => fetchApi("/health/readiness"),
  getTelemetry: () => fetchApi("/health/telemetry"),

  // Analytics
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

  // Models & Registry
  getModelRegistry: () => fetchApi("/models/registry"),
  evaluateAllModels: () => fetchApi("/models/evaluate-all"),
  getModelFeatureImportance: (name) => fetchApi(`/models/${name}/feature-importance`),
  checkModelDrift: (name, metric) => fetchApi(`/models/${name}/drift?current_metric=${metric}`),

  // AI Content Tools
  analyzeSentiment: (text) => fetchApi("/ai/sentiment/analyze", { method: "POST", body: JSON.stringify({ text }) }),
  analyzeCaption: (text, platform) => fetchApi("/ai/caption/analyze", { method: "POST", body: JSON.stringify({ text, platform }) }),
  optimizeCaption: (text, platform, tone) => fetchApi("/ai/caption/optimize", { method: "POST", body: JSON.stringify({ text, platform, target_tone: tone }) }),
  recommendHashtags: (text, platform, topK = 5) => fetchApi("/ai/hashtags/recommend", { method: "POST", body: JSON.stringify({ text, platform, top_k: topK }) }),

  // Scheduling
  recommendTimes: (data) => fetchApi("/scheduling/recommend-times", { method: "POST", body: JSON.stringify(data) }),

  // Auto-Reply
  classifyComment: (text) => fetchApi("/reply/classify", { method: "POST", body: JSON.stringify({ text }) }),
  suggestReply: (text, id) => fetchApi("/reply/suggest", { method: "POST", body: JSON.stringify({ comment_text: text, comment_id: id }) }),

  // Growth Predictions
  predictGrowth: (data) => fetchApi("/growth/predict", { method: "POST", body: JSON.stringify(data) }),
};
