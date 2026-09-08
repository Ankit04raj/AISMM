"""Persist recommendation feedback scoped to user."""
from alembic import op
import sqlalchemy as sa
from backend.app.db.models import GUID
revision='6e7f8a9b0c1d'
down_revision='5d6e7f8a9b0c'
branch_labels=depends_on=None

def upgrade():
    op.create_table('strategy_feedback', sa.Column('id',GUID(),primary_key=True),
        sa.Column('user_id',GUID(),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('recommendation_id',sa.String(255),nullable=False),sa.Column('applied',sa.Boolean(),nullable=False),
        sa.Column('feedback_notes',sa.Text()),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_strategy_feedback_user_id','strategy_feedback',['user_id'])

def downgrade():
    op.drop_table('strategy_feedback')
