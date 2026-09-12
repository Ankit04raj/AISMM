# AISMM Staging & Production Deployment Runbook

**Document Version:** 1.0.0  
**Last Updated:** 2026-09-09 (Asia/Kolkata)  
**Target Architecture:** FastAPI (Python 3.13) + React 18 (Vite/Nginx) + PostgreSQL 16 + Redis 7  

---

## 1. Pre-Deployment Infrastructure Prerequisites

Before initiating any deployment or migration:
1. **Isolated PostgreSQL 16 Instance**: Ensure a dedicated database (`aismm`) is provisioned with a secure high-entropy password. Never reuse default passwords from older documentation.
2. **Redis 7 Instance**: Required for production rate limiting (`REDIS_URL=redis://redis:6379/0`).
3. **Dedicated Encryption Master Key (`SECRET_KEY`)**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
   **CRITICAL:** Back up `SECRET_KEY`. If this key is lost or regenerated, all existing social account tokens and TOTP secrets stored in the database become permanently unrecoverable.
4. **Dedicated JWT Signing Key (`JWT_SECRET_KEY`)**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
5. **Reverse Proxy (Nginx / Cloudflare)**:
   - Terminate SSL/TLS with HSTS enabled.
   - Forward client IP headers safely (`X-Forwarded-For`, `X-Forwarded-Proto`).
   - Restrict direct public access to ports `8000` (backend API), `5432` (PostgreSQL), and `6379` (Redis). Only expose port `3000` (frontend / Nginx proxy).

---

## 2. Production Environment Variable Checklist (`.env`)

```env
# Runtime
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Security & Cryptography
SECRET_KEY=<GENERATED_48_CHAR_SECRET_KEY>
JWT_SECRET_KEY=<GENERATED_48_CHAR_JWT_KEY>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=60
BCRYPT_ROUNDS=12

# Database & Cache
DATABASE_URL=postgresql+asyncpg://aismm_user:<DB_PASSWORD>@postgres:5432/aismm
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_ECHO=false
REDIS_URL=redis://redis:6379/0

# Web & Origins
FRONTEND_URL=https://app.your-domain.com
CORS_ORIGINS=["https://app.your-domain.com"]

# Email & Notifications (Required in production)
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<YOUR_SMTP_API_KEY>
FROM_EMAIL=noreply@your-domain.com
FROM_NAME=AISMM

# Social Media OAuth (Register callback: https://app.your-domain.com/oauth/callback)
X_CLIENT_ID=<TWITTER_OAUTH2_CLIENT_ID>
X_CLIENT_SECRET=<TWITTER_OAUTH2_CLIENT_SECRET>
LINKEDIN_CLIENT_ID=<LINKEDIN_CLIENT_ID>
LINKEDIN_CLIENT_SECRET=<LINKEDIN_CLIENT_SECRET>
YOUTUBE_CLIENT_ID=<GOOGLE_CLIENT_ID>
YOUTUBE_CLIENT_SECRET=<GOOGLE_CLIENT_SECRET>

# Security Host Allowlist
MEDIA_ALLOWED_HOSTS=["cdn.your-domain.com", "storage.googleapis.com", "s3.amazonaws.com"]
```

---

## 3. Step-by-Step Staging & Production Deployment Procedure

### Step 1: Clone and Inspect
```bash
git clone https://github.com/Ankit04raj/AISMM.git
cd AISMM
git checkout main
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env and populate production credentials
chmod 600 .env
```

### Step 3: Run Database Migrations
Always run database migrations and verify the head revision before launching user-facing traffic:
```bash
docker compose run --rm migrate
```
Verify output shows:
```
Running upgrade -> 1c2e5404a0b3
...
Running upgrade 5d6e7f8a9b0c -> 6e7f8a9b0c1d (head)
```

### Step 4: Build and Start Containers
```bash
docker compose build --no-cache
docker compose up -d
```

### Step 5: Post-Deployment Smoke Verification
```bash
# Verify container health
docker compose ps

# Run automated HTTP smoke checks
TEST_API_URL=https://app.your-domain.com/api/v1 python scripts/verify_postgres.py
```

---

## 4. PostgreSQL Backup, Restore & Disaster Recovery

### Automated Backup
```bash
# Daily snapshot
docker compose exec postgres pg_dump -U aismm -d aismm -F c -b -v -f /var/lib/postgresql/data/aismm_backup_$(date +%Y%m%d_%H%M%S).dump
```

### Restore Rehearsal
```bash
# To restore to a clean database:
docker compose exec postgres pg_restore -U aismm -d aismm -v /var/lib/postgresql/data/aismm_backup_XXXX.dump
```

---

## 5. Rollback Plan

1. **Application Rollback**:
   ```bash
   git checkout <PREVIOUS_STABLE_TAG>
   docker compose build backend frontend
   docker compose up -d
   ```
2. **Schema Rollback Considerations**:
   - **Warning:** Migration `5d6e7f8a9b0c` introduces encrypted session hashes and Fernet credential fields. Never blindly downgrade migrations with `alembic downgrade` if production data was created under the new schema.
   - If a rollback is required, restore the database from the pre-deployment pg_dump snapshot.

---

## 6. Launch Acceptance Gates

- [ ] **SMTP Live Verification**: Real email received for registration verification and password reset.
- [ ] **Social Provider App Approval**: Production redirect URI (`https://app.your-domain.com/oauth/callback`) registered in Twitter Developer Portal, LinkedIn Developer Portal, and Google Cloud Console.
- [ ] **Fail-Closed Rate Limiting**: Verified rate limiter triggers HTTP 429 when threshold is reached and fails closed on Redis outage.
- [ ] **HTTPS & Security Headers**: Verified CSP, HSTS, X-Content-Type-Options, and X-Frame-Options headers present on all responses.
- [ ] **Data Encryption**: Confirmed zero plaintext access tokens in database tables.
