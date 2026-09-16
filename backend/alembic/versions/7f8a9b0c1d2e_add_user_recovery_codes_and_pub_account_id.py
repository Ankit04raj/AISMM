"""add two_factor_recovery_codes to users and account_id to post_publications

Revision ID: 7f8a9b0c1d2e
Revises: 6e7f8a9b0c1d
Create Date: 2026-09-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from backend.app.db.models import GUID

# revision identifiers, used by Alembic.
revision = '7f8a9b0c1d2e'
down_revision = '6e7f8a9b0c1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check users table columns
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'two_factor_recovery_codes' not in user_columns:
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('two_factor_recovery_codes', sa.JSON(), nullable=True))

    # Check post_publications table columns
    pub_columns = [col['name'] for col in inspector.get_columns('post_publications')]
    if 'account_id' not in pub_columns:
        with op.batch_alter_table('post_publications') as batch_op:
            batch_op.add_column(sa.Column('account_id', GUID(), nullable=True))
            batch_op.create_index('ix_post_publications_account_id', ['account_id'])


def downgrade() -> None:
    with op.batch_alter_table('post_publications') as batch_op:
        batch_op.drop_index('ix_post_publications_account_id')
        batch_op.drop_column('account_id')

    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('two_factor_recovery_codes')
