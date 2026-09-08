"""Durable sessions, OAuth state, recovery, and credential encryption.

Back up database AND SECRET_KEY before upgrading. Existing sessions are invalidated.
"""
from alembic import op
import sqlalchemy as sa
from backend.app.db.models import GUID

revision = '5d6e7f8a9b0c'
down_revision = '4c5d6e7f8a9b'
branch_labels = depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch:
        batch.add_column(sa.Column('two_factor_secret', sa.Text(), nullable=True))
        batch.add_column(sa.Column('two_factor_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column('terms_accepted_at', sa.DateTime()))
        batch.add_column(sa.Column('password_reset_hash', sa.String(64)))
        batch.add_column(sa.Column('password_reset_expiry', sa.DateTime()))
        batch.add_column(sa.Column('two_factor_last_step', sa.Integer()))
        batch.create_index('ix_users_password_reset_hash', ['password_reset_hash'])
    op.create_table('auth_sessions',
        sa.Column('id', sa.String(64), primary_key=True),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('refresh_hash', sa.String(64), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_table('oauth_attempts',
        sa.Column('state_hash', sa.String(64), primary_key=True),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(32), nullable=False),
        sa.Column('redirect_uri', sa.Text(), nullable=False),
        sa.Column('verifier', sa.Text()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('consumed', sa.Boolean(), nullable=False, server_default=sa.false()))
    # Encrypt existing secrets without bringing plaintext into logs.
    from backend.app.core.vault import SecretVault
    vault = SecretVault()
    conn = op.get_bind()
    for table, fields in [('users', ['two_factor_secret']), ('social_accounts', ['access_token', 'refresh_token'])]:
        for row in conn.execute(sa.text(f"SELECT id, {', '.join(fields)} FROM {table}")).mappings():
            for field in fields:
                value = row[field]
                if value and not value.startswith('v2$'):
                    conn.execute(sa.text(f'UPDATE {table} SET {field}=:value WHERE id=:id'),
                                 {'value': vault.encrypt(value), 'id': row['id']})


def downgrade():
    # Intentionally do not decrypt credential columns on rollback.
    op.drop_table('oauth_attempts')
    op.drop_table('auth_sessions')
    with op.batch_alter_table('users') as batch:
        batch.drop_index('ix_users_password_reset_hash')
        for name in ['two_factor_last_step', 'password_reset_expiry', 'password_reset_hash', 'terms_accepted_at']:
            batch.drop_column(name)
