# AISMM — Durable Architectural Memory & Engineering Decisions

**Document Version:** 1.0.0  
**Status:** Permanent Reference  

---

## 1. Key Architectural Decisions (ADR Summary)

### ADR-01: Platform-Agnostic Core & Capability Matrix
- **Decision**: The core business, scheduling, AI, and analytics services must never have platform branching (`if instagram: ...`). All platform behavior is accessed via `BasePlatformAdapter` instances dynamically registered in `PlatformRegistry`.
- **Why**: Allows seamless onboarding of new platforms (e.g. TikTok, Pinterest, Threads) with zero core engine modifications.
- **Enforcement**: Automated unit tests assert that `PlatformRegistry` dynamically discovers adapters without hardcoded registry lists.

### ADR-02: Tenant-Isolated Adapter Factory (`owned_adapter`)
- **Decision**: Platform adapters are never global singletons. The `owned_adapter(db, user_id, platform, account_id)` async factory instantiates adapters on-demand with decrypted credentials strictly scoped to the requesting user.
- **Why**: Eliminates cross-tenant credential leakage and race conditions in concurrent multi-user environments.

### ADR-03: ORM Boundary Encryption (`EncryptedText` & `SecretVault`)
- **Decision**: All OAuth access tokens, refresh tokens, and TOTP MFA secrets are encrypted before persistence in PostgreSQL/SQLite using Fernet AES-256 with PBKDF2 key derivation (100k rounds) and stored with `v2$` envelope prefixes.
- **Why**: Ensures database dumps or unprivileged database access cannot expose third-party access tokens or multi-factor authentication secrets.

### ADR-04: Single-Use Refresh Token Rotation & Session Management
- **Decision**: Refresh tokens are stored in the database as SHA-256 hashes inside the `AuthSession` model. When an access token is refreshed, the existing session row is atomically updated with a new refresh token hash, invalidating the previous token.
- **Why**: Prevents refresh token replay and session hijacking attacks.

### ADR-05: Server-Side `OtpChallenge` Tracking
- **Decision**: OTPs generated for email verification and password resets are stored in an `OtpChallenge` table with cryptographic SHA-256 hashes, 5-minute expirations, and max 5 attempt limits.
- **Why**: Prevents brute-force guessing and enables reliable audit trails for verification workflows.

### ADR-06: Atomic Scheduler Dispatch with Row Locking
- **Decision**: The background scheduler claims due posts using atomic database updates (`UPDATE schedules SET status='publishing' WHERE id=:id AND status='pending'`) before initiating network requests.
- **Why**: Guarantees at-most-once execution and prevents duplicate publishing when multiple worker processes run concurrently.

### ADR-07: Dual Database Support (PostgreSQL 16 & SQLite 3)
- **Decision**: Implement custom `GUID` TypeDecorator that renders native `UUID` on Postgres and `CHAR(36)` on SQLite.
- **Why**: Enables instantaneous local developer onboarding and rapid pytest execution with SQLite in-memory, while maintaining production performance on PostgreSQL 16.

---

## 2. Hard Constraints & Operational Discoveries

1. **Bcrypt 72-Byte Truncation Constraint**:
   - `bcrypt` silently ignores bytes beyond 72 UTF-8 bytes. `RegisterRequest`, `UserLoginRequest`, and `PasswordChange` enforce `len(password.encode("utf-8")) <= 72` at Pydantic validation boundaries to prevent bypasses.

2. **Frontend 401 Refresh Mutex**:
   - Multiple concurrent API requests hitting 401 Unauthorized must not trigger multiple concurrent `/auth/refresh` calls (which would invalidate rotating refresh hashes). The `fetchApi` client implements a single-flight promise mutex `refreshSession()`.

3. **Production Email OTP Suppression**:
   - In development mode without SMTP, the OTP may be returned in the response object solely for local testing. In production (`ENVIRONMENT="production"`), the token is strictly suppressed from all API responses, and the endpoint fails with HTTP 502 if SMTP delivery fails.

4. **Zero-Mock Policy on Analytics & Telemetry**:
   - Empty connected accounts must render zero metrics or clean empty state illustrations. Extrapolating synthetic follower graphs or mock revenue numbers is strictly prohibited.
