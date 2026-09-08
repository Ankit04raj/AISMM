"""add phone verification fields to users table

Revision ID: 4c5d6e7f8a9b
Revises: 3b4c5d6e7f8a
Create Date: 2026-09-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4c5d6e7f8a9b'
down_revision = '3b4c5d6e7f8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add phone verification fields to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('phone_verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('phone_verification_token', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('phone_verification_expiry', sa.DateTime(), nullable=True))
    # Create index on phone_number
    op.create_index('ix_users_phone_number', 'users', ['phone_number'], unique=True)


def downgrade() -> None:
    # Remove phone verification fields
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index('ix_users_phone_number')
        batch_op.drop_column('phone_verification_token')
        batch_op.drop_column('phone_verification_expiry')
        batch_op.drop_column('phone_verified')
        batch_op.drop_column('phone_number')