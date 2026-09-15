---
name: priority-2.3-token-cookie-transition
description: HttpOnly cookie transition for auth tokens — remove localStorage, backend sets cookies, frontend reads via fetch creds, mutex preserved
metadata:
  type: project
---

# Priority 2.3 — Token Storage Hardening: HttpOnly Cookie Transition

**Current state (verified in client.js lines 9-24, 39-48):**
- `getAuthToken()` / `setAuthSession()` / `clearAuthSession()` use `localStorage` (`aismm_access_token`, `aismm_refresh_token`, `aismm_user`)
- `refreshSession()` reads `localStorage.getItem('aismm_refresh_token')`
- `fetchApi()` sends `Authorization: Bearer ${token}` header
- `logout()` sends refresh token in JSON body
- Single-flight mutex `refreshInFlight` uses `localStorage.getItem('aismm_refresh_token')`

**Runbook direction:** Planned transition to HttpOnly, Secure, SameSite cookies set by backend.

**Transition design (direct — no subagents):**

1. **Backend — cookie setting** (`auth.py` login/refresh endpoints):
   - After token generation (line 135/178 etc.), set response cookies:
     - `aismm_access_token` (HttpOnly, Secure, SameSite=Lax or Strict, max-age based on JWT expiry)
     - `aismm_refresh_token` (HttpOnly, Secure, SameSite=Lax/Strict, longer max-age)
   - Remove `verification_token` from response data (already done — G-11)
   - Return minimal response (user profile only, no tokens in JSON body)

2. **Frontend — remove localStorage** (`frontend/src/api/client.js`):
   - Replace `getAuthToken()` → return `""` (cookie is sent automatically by browser with `credentials: 'include'`)
   - Replace `setAuthSession()` → no-op (cookies handled by backend response headers); keep user storage optional (`aismm_user` can remain if needed for UI — not XSS-sensitive, but recommend session-only)
   - Replace `clearAuthSession()` → call `/auth/logout` (which clears cookies server-side) + remove user storage
   - Replace `refreshSession()` → POST `/auth/refresh` with `credentials: 'include'` (no body token needed — cookie carries it); read new access token from response cookie, not body
   - Update `fetchApi()` → add `credentials: 'include'` to fetch; remove manual `Authorization` header (cookie carries it); keep `token ? { Authorization... }` as fallback for dev/non-cookie environments but default to cookie-only
   - Update `logout()` → POST `/auth/logout` with `credentials: 'include'`; no JSON body needed

3. **Mutex preservation:** `refreshInFlight` stays — it guards the refresh request itself, independent of token storage mechanism. The refresh now reads nothing from localStorage; it just sends the cookie-backed POST.

4. **Cross-origin / CORS:** Cookies require `CORS_ORIGINS` to include frontend origin and backend must respond with `Access-Control-Allow-Credentials: true`. Check `settings.py` CORS config.

**Status:** Design documented. Implementation requires both backend cookie headers + frontend removal — multi-file, must stay coordinated. Blocking: need backend cookie-setting code in auth endpoints.
