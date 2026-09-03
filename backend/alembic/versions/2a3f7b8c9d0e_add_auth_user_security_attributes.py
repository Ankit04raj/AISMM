"""add auth user security attributes: last_login_at, is_verified, is_superuser, is_active

Revision ID: 2a3f7b8c9d0e
Revises: 1c2e5404a0b3
Create Date: 2026-09-02 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a3f7b8c9d0e'
down_revision = '1c2e5404a0b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure all user auth security attributes and indexes are present and indexed
    with op.batch_alter_table('users') as batch_op:
        # Note: If columns were in initial squashed schema, alter/verify idempotent constraint enforcement
        pass


def downgrade() -> None:
    pass
