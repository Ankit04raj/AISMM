"""Generate local-only secrets. Never overwrite existing configuration."""
from pathlib import Path
import secrets
path=Path('.env')
if path.exists():
    raise SystemExit('.env already exists; left unchanged.')
path.write_text('ENVIRONMENT=development\nSECRET_KEY='+secrets.token_urlsafe(48)+'\nJWT_SECRET_KEY='+secrets.token_urlsafe(48)+'\nDATABASE_URL=sqlite+aiosqlite:///./aismm.dev.db\nFRONTEND_URL=http://localhost:5173\nENABLE_EMAIL_NOTIFICATIONS=false\nENABLE_PHONE_VERIFICATION=false\n')
path.chmod(0o600)
print('Created local .env. Email delivery is disabled; never use this configuration in production.')
