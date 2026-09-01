"""initial schema: users, social_accounts, posts, post_media, post_publications, comments, metrics, schedules, ml_models, model_predictions, sentiment_analyses

Revision ID: 1c2e5404a0b3
Revises:
Create Date: 2026-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1c2e5404a0b3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. social_accounts
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('platform_user_id', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('account_metadata', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('connected_at', sa.DateTime(), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('platform', 'platform_user_id', name='uq_platform_user'),
    )
    op.create_index('ix_social_accounts_user_id', 'social_accounts', ['user_id'])
    op.create_index('ix_social_accounts_platform', 'social_accounts', ['platform'])
    op.create_index('ix_social_accounts_platform_user_id', 'social_accounts', ['platform_user_id'])
    op.create_index('ix_social_accounts_user_platform', 'social_accounts', ['user_id', 'platform'])

    # 3. posts
    content_type_enum = sa.Enum('POST', 'REEL', 'STORY', 'CAROUSEL', name='contenttypeenum')
    post_status_enum = sa.Enum('DRAFT', 'SCHEDULED', 'PUBLISHING', 'PUBLISHED', 'FAILED', 'CANCELLED', 'DELETED', name='poststatusenum')

    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content_type', content_type_enum, nullable=False, default='POST'),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('hashtags', sa.JSON(), nullable=True),
        sa.Column('mentions', sa.JSON(), nullable=True),
        sa.Column('status', post_status_enum, nullable=False, default='DRAFT'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('platform_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_posts_user_id', 'posts', ['user_id'])
    op.create_index('ix_posts_status', 'posts', ['status'])
    op.create_index('ix_posts_scheduled_at', 'posts', ['scheduled_at'])
    op.create_index('ix_posts_user_status', 'posts', ['user_id', 'status'])
    op.create_index('ix_posts_user_scheduled', 'posts', ['user_id', 'scheduled_at'])

    # 4. post_media
    op.create_table(
        'post_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_type', sa.String(length=20), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('caption', sa.Text(), nullable=True),
        sa.Column('alt_text', sa.String(length=1000), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_post_media_post_id', 'post_media', ['post_id'])

    # 5. post_publications
    op.create_table(
        'post_publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('platform_post_id', sa.String(length=100), nullable=True),
        sa.Column('platform_container_id', sa.String(length=100), nullable=True),
        sa.Column('permalink', sa.String(length=500), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('platform_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('post_id', 'platform', name='uq_post_platform'),
    )
    op.create_index('ix_post_publications_post_id', 'post_publications', ['post_id'])
    op.create_index('ix_post_publications_platform', 'post_publications', ['platform'])
    op.create_index('ix_post_publications_platform_post_id', 'post_publications', ['platform_post_id'])
    op.create_index('ix_post_publications_platform_post', 'post_publications', ['platform', 'platform_post_id'])

    # 6. comments
    op.create_table(
        'comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('platform_comment_id', sa.String(length=100), nullable=True),
        sa.Column('parent_comment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('comments.id'), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('like_count', sa.Integer(), nullable=True, default=0),
        sa.Column('is_hidden', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_comments_post_id', 'comments', ['post_id'])

    # 7. metrics
    op.create_table(
        'metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('metrics', sa.JSON(), nullable=False),
        sa.Column('fetched_at', sa.DateTime(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=True),
    )
    op.create_index('ix_metrics_post_id', 'metrics', ['post_id'])
    op.create_index('ix_metrics_platform', 'metrics', ['platform'])
    op.create_index('ix_metrics_entity_id', 'metrics', ['entity_id'])
    op.create_index('ix_metrics_fetched_at', 'metrics', ['fetched_at'])
    op.create_index('ix_metrics_platform_entity', 'metrics', ['platform', 'entity_id', 'entity_type'])
    op.create_index('ix_metrics_post_fetched', 'metrics', ['post_id', 'fetched_at'])

    # 8. schedules
    op.create_table(
        'schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False, default='UTC'),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('next_attempt_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_schedules_user_id', 'schedules', ['user_id'])
    op.create_index('ix_schedules_post_id', 'schedules', ['post_id'])
    op.create_index('ix_schedules_scheduled_at', 'schedules', ['scheduled_at'])
    op.create_index('ix_schedules_user_scheduled', 'schedules', ['user_id', 'scheduled_at'])
    op.create_index('ix_schedules_status_next', 'schedules', ['status', 'next_attempt_at'])

    # 9. ml_models
    op.create_table(
        'ml_models',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('framework', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('artifact_path', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_production', sa.Boolean(), nullable=False, default=False),
        sa.Column('trained_at', sa.DateTime(), nullable=True),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('name', 'version', name='uq_model_version'),
    )
    op.create_index('ix_ml_models_name', 'ml_models', ['name'])

    # 10. model_predictions
    op.create_table(
        'model_predictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ml_models.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('prediction', sa.JSON(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_model_predictions_model_id', 'model_predictions', ['model_id'])
    op.create_index('ix_model_predictions_entity_id', 'model_predictions', ['entity_id'])
    op.create_index('ix_model_predictions_created', 'model_predictions', ['created_at'])
    op.create_index('ix_predictions_model_entity', 'model_predictions', ['model_id', 'entity_id', 'entity_type'])

    # 11. sentiment_analyses
    op.create_table(
        'sentiment_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('scores', sa.JSON(), nullable=True),
        sa.Column('entities', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_sentiment_analyses_post_id', 'sentiment_analyses', ['post_id'])


def downgrade() -> None:
    op.drop_table('sentiment_analyses')
    op.drop_table('model_predictions')
    op.drop_table('ml_models')
    op.drop_table('schedules')
    op.drop_table('metrics')
    op.drop_table('comments')
    op.drop_table('post_publications')
    op.drop_table('post_media')
    op.drop_table('posts')
    op.drop_table('social_accounts')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS contenttypeenum')
    op.execute('DROP TYPE IF EXISTS poststatusenum')
