# Run and deploy AISMM

**Current status: substantial implementation complete and locally verified; not approved for public production launch.** Read `IMPLEMENTATION_REPORT.md` before deployment. Live provider approval, delivery tests, legal setup, and infrastructure acceptance remain required.

## Local development

Requirements: Python 3.13, Node 24, npm. Run from the repository root.

```bash
python scripts/init_local.py
make install
make migrate
make run-backend
# In a second terminal:
make run-frontend
```

Open `http://localhost:5173`. Create a test account; local development returns a clearly labeled verification token when email delivery is disabled. This is not proof that an email was delivered. Never use the generated development configuration for real users. Phone/SMS is not offered in the current registration UI.

The initial database is empty. No connected accounts, posts, comments, or audience metrics are seeded. Composer drafts remain in session storage in the same browser tab. Registration, verification, settings, routes, analytics reads, and logout work without social credentials. Publishing requires an owned connected account.

## Verification

```bash
make test
npm --prefix frontend run build
npm --prefix frontend run lint
# Optional known-vulnerability checks:
.venv/bin/pip install pip-audit
.venv/bin/pip-audit -r backend/requirements.txt
npm --prefix frontend audit
```

The backend suite includes isolated SQLite database tests; provider transport tests are mocked and are not live-platform acceptance tests. `docs/verification/` contains the fresh command outputs from this pass.

For browser verification, first build the frontend and start the local backend on port 8000. Connect an existing Chromium debugging session through `AGENT_BROWSER_CDP`, then run `node scripts/verify_browser.cjs`. The script routes a private test origin to the local built files and real local API, creates disposable development accounts, checks navigation/drafts/logout, and captures desktop and mobile screenshots. **Do not run this against a customer environment.** Screenshots can include test profile data or authenticator setup; do not publish unreviewed artifacts.

## Production configuration

1. Back up your database and existing encryption/signing keys. Losing `SECRET_KEY` makes encrypted credentials unrecoverable. Do not casually regenerate it during deployments.
2. Copy `.env.example` to `.env`. Configure independent high-entropy master/JWT secrets, a database password, HTTPS frontend origin, explicit CORS origins, and working SMTP credentials/from address.
3. Confirm the legal operator, support/privacy contact, jurisdiction, retention policy, subprocessors, and reviewed Terms/Privacy pages. Current pages are implementation drafts, not final legal approval.
4. Keep the database, Redis, and backend off the public Internet. The supplied Compose file exposes only the frontend on `127.0.0.1:3000`.
5. Put an HTTPS reverse proxy/load balancer in front of that frontend. Configure DNS, certificates, HSTS, trusted proxy IP handling, and request/body limits. Never blindly trust client-supplied forwarded headers. Nginx forwards its observed client IP; configure trusted edge real-IP handling if another proxy is in front, otherwise clients may share an IP-based rate-limit bucket.
6. Set `MEDIA_ALLOWED_HOSTS` only to operator-controlled public HTTPS storage hosts. No local upload/storage pipeline is implemented. Do not approve redirectors or domains that can resolve to private infrastructure.
7. Configure provider apps and register exactly `https://YOUR-DOMAIN/oauth/callback`. X, LinkedIn, and YouTube have authenticated, expiring, one-use OAuth state with server-side credential storage. Actual permissions, publish formats, refresh/revocation, rate limits, and app review must still be exercised live. **Meta (Instagram/Facebook) connections are disabled pending API modernization and Page/business-account selection.**

```bash
docker compose build
docker compose up -d
# Migration must finish successfully before the API becomes healthy:
docker compose logs migrate
docker compose ps
```

The migration service runs Alembic before the backend. Fresh SQLite and PostgreSQL migrations were run in this pass. Existing deployment upgrade/rollback must be rehearsed from a real backup; migration 5 encrypts legacy credential values and introduces durable sessions/MFA. Existing tokens without a durable session ID require a new login. Never stamp a database as migrated without verifying its schema.

Docker images and Compose orchestration were repaired but not built/executed in this environment. PostgreSQL and Redis were tested as local services, separately from Compose.

## Production launch acceptance gates

- SMTP delivery to real mailboxes, verification expiry/resend and account recovery.
- Each platform's real OAuth app approval and callback, ownership validation, token expiry/refresh/revocation, actual publishing and deletion, comment sync/reply, and API failure behavior.
- Meta implementation before making those connect buttons available.
- Shared Redis rate limiting and fail-closed behavior; trusted proxy IP configuration.
- HTTPS/CSP/CORS in the deployed environment; no secrets in bundles, logs, traces, or backups.
- Browser accessibility/keyboard review beyond the automated responsive checks; remaining lint warnings reviewed.
- Deployment-specific load testing, task timeouts, backups/restores, monitoring, incident alerting, log retention, and security review.
- Real-data model evaluation before presenting experimental ML as validated business forecasts.

## Scheduler operations

Scheduled content is stored locally without calling a provider's schedule/publish API early. Workers atomically claim due records and commit the claim **before** external publishing. This prevents two workers from intentionally processing the same pending record. It does not create an exactly-once transaction with a social platform.

A process/network interruption can leave a schedule in `publishing` or a publication marked failed even when the provider accepted a request. Inspect the destination platform before retrying. There is deliberately no blind retry of interrupted claims. Add provider idempotency where available and an operator recovery procedure before high-volume launch.

## Known unavailable features

Workspace API keys, custom notification preferences, direct-message inbox aggregation, media-file uploads, unattended auto-reply dispatch, independently validated growth-drift history, and production model-training operations are not complete. The UI/API should identify these as unavailable or experimental rather than simulate success.
