"""Create otp_challenge and oauth_states tables, and add email_verified_at to users."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect
from backend.app.db.models import GUID


revision = '9b8c1e2f3a4d'
down_revision = '8a9b0c1d2e3f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = inspect(conn)

    # 1. Add email_verified_at column to users table if not exists
    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'email_verified_at' not in user_cols:
        with op.batch_alter_table('users') as batch_op:
            batch_op.add_column(sa.Column('email_verified_at', sa.DateTime(), nullable=True))

    # 2. Create otp_challenges table if not exists
    tables = inspector.get_table_names()
    if 'otp_challenges' not in tables:
        op.create_table(
            'otp_challenges',
            sa.Column('id', GUID(), nullable=False, primary_key=True),
            sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('purpose', sa.String(length=32), nullable=False),
            sa.Column('otp_hash', sa.String(length=64), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.Column('revoked_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        )
        op.create_index('ix_otp_challenges_email', 'otp_challenges', ['email'])
        op.create_index('ix_otp_challenges_purpose', 'otp_challenges', ['purpose'])
        op.create_index('ix_otp_challenges_user_id', 'otp_challenges', ['user_id'])

    # 3. Create oauth_states table if not exists
    if 'oauth_states' not in tables:
        op.create_table(
            'oauth_states',
            sa.Column('id', GUID(), nullable=False, primary_key=True),
            sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('platform', sa.String(length=32), nullable=False),
            sa.Column('state', sa.String(length=128), nullable=False),
            sa.Column('code_verifier', sa.Text(), nullable=True),
            sa.Column('nonce', sa.String(length=128), nullable=True),
            sa.Column('redirect_uri', sa.Text(), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('consumed', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=text('CURRENT_TIMESTAMP')),
        )
        op.create_index('ix_oauth_states_user_id', 'oauth_states', ['user_id'])
        op.create_index('ix_oauth_states_platform', 'oauth_states', ['platform'])
        op.create_index('ix_oauth_states_state', 'oauth_states', ['state'], unique=True)


def downgrade():
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()

    if 'oauth_states' in tables:
        op.drop_index('ix_oauth_states_state', table_name='oauth_states')
        op.drop_index('ix_oauth_states_platform', table_name='oauth_states')
        op.drop_index('ix_oauth_states_user_id', table_name='oauth_states')
        op.drop_table('oauth_states')

    if 'otp_challenges' in tables:
        op.drop_index('ix_otp_challenges_user_id', table_name='otp_challenges')
        op.drop_index('ix_otp_challenges_purpose', table_name='otp_challenges')
        op.drop_index('ix_otp_challenges_email', table_name='otp_challenges')
        op.drop_table('otp_challenges')

    user_cols = [c['name'] for c in inspector.get_columns('users')]
    if 'email_verified_at' in user_cols:
        with op.batch_alter_table('users') as batch_op:
            batch_op.drop_column('email_verified_at')
