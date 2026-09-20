/** Server-owned connection_status presentation. Do not infer live from tokens or metadata. */

const STATUS_RANK = { connected_live: 0, token_expired: 1, disconnected: 2 };

const STATUS_LABELS = {
  connected_live: "Connected (Live)",
  token_expired: "Token Expired",
  disconnected: "Disconnected",
};

export function normalizeConnectionStatus(status) {
  if (status === "connected_live" || status === "token_expired") return status;
  return "disconnected";
}

export function labelForConnectionStatus(status) {
  return STATUS_LABELS[normalizeConnectionStatus(status)];
}

export function selectAccountForPlatform(accounts, platform) {
  const key = (platform || "").toLowerCase();
  const matches = (accounts || []).filter((a) => (a.platform || "").toLowerCase() === key);
  return matches.slice().sort((a, b) => {
    const ra = STATUS_RANK[normalizeConnectionStatus(a.connection_status)] ?? 2;
    const rb = STATUS_RANK[normalizeConnectionStatus(b.connection_status)] ?? 2;
    return ra - rb;
  })[0];
}

export function shouldOfferReconnect(status) {
  const normalized = normalizeConnectionStatus(status);
  return normalized === "token_expired" || normalized === "disconnected";
}
