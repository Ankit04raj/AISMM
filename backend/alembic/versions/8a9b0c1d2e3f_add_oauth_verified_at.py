"""add oauth_verified_at to social_accounts

Records the timestamp of the last successful real OAuth exchange + profile
fetch. Legacy rows keep NULL and render as disconnected until reconnected.

Revision ID: 8a9b0c1d2e3f
Revises: 7f8a9b0c1d2e
Create Date: 2026-09-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8a9b0c1d2e3f'
down_revision = '7f8a9b0c1d2e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('social_accounts')]
    if 'oauth_verified_at' not in columns:
        with op.batch_alter_table('social_accounts') as batch_op:
            batch_op.add_column(sa.Column('oauth_verified_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('social_accounts') as batch_op:
        batch_op.drop_column('oauth_verified_at')
