"""add email verification fields to users table

Revision ID: 3b4c5d6e7f8a
Revises: 2a3f7b8c9d0e
Create Date: 2026-09-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3b4c5d6e7f8a'
down_revision = '2a3f7b8c9d0e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add email verification token and expiry columns to users table
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('email_verification_token', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('email_verification_expiry', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove email verification fields
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('email_verification_token')
        batch_op.drop_column('email_verification_expiry')