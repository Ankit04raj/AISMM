"""Owner-scoped comment inbox and provider actions."""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models import User, Post, PostPublication, Comment
from backend.app.api.deps import get_current_verified_user
from backend.app.core.schemas.post import ReplyToCommentRequest
from backend.app.services.owned_adapter import owned_adapter

router = APIRouter(prefix='/comments', tags=['Comments'])


async def own_comment(db, user, platform, comment_id):
    try: key=UUID(comment_id)
    except ValueError: raise HTTPException(404, 'Comment not found')
    record = await db.scalar(select(Comment).join(Post).where(
        Comment.id==key, Comment.platform==platform, Post.user_id==user.id))
    if not record:
        raise HTTPException(404, 'Comment not found')
    return record


@router.get('')
async def inbox(limit: int = Query(100, ge=1, le=100), current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).join(Post).where(Post.user_id==current_user.id).order_by(Comment.created_at.desc()).limit(limit))
    return {'comments': [{'id':str(c.id), 'platform':c.platform, 'text':c.text, 'author_name':c.username,
                         'created_at':c.created_at.isoformat(), 'type':'comment', 'postId':str(c.post_id)} for c in result.scalars()]}


@router.post('/sync')
async def sync_inbox(current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PostPublication).join(Post).where(
        Post.user_id==current_user.id, PostPublication.platform_post_id.is_not(None)
    ).order_by(PostPublication.created_at.desc()).limit(50))
    targets = [(p.platform, str(p.post_id)) for p in result.scalars()]
    errors = []
    for platform, post_id in targets:
        try:
            await list_comments(platform, post_id, 50, current_user, db)
        except Exception:
            await db.rollback()
            errors.append(f'{platform}: comments could not be synchronized; check connection and permissions.')
    return {'processed_posts':len(targets), 'errors':errors}


@router.get('/posts/{platform}/{post_id}')
async def list_comments(platform: str, post_id: str, limit: int = Query(50, ge=1, le=100), current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    try: key=UUID(post_id)
    except ValueError: raise HTTPException(404, 'Post not found')
    publication = await db.scalar(select(PostPublication).join(Post).where(
        Post.id==key, Post.user_id==current_user.id, PostPublication.platform==platform))
    if not publication or not publication.platform_post_id:
        raise HTTPException(404, 'Published post not found')
    adapter = await owned_adapter(db, current_user.id, platform)
    records = await adapter.get_comments(publication.platform_post_id, limit=limit)
    for c in records:
        existing = await db.scalar(select(Comment).where(Comment.post_id==key, Comment.platform==platform, Comment.platform_comment_id==c.id))
        if existing: existing.text=c.text
        else: db.add(Comment(post_id=key, platform=platform, platform_comment_id=c.id, text=c.text, username=c.author_name,
                             created_at=c.created_at.replace(tzinfo=None) if c.created_at else None))
    await db.commit()
    return await inbox(limit, current_user, db)


@router.post('/{platform}/{comment_id}/reply')
async def reply_to_comment(platform: str, comment_id: str, request: ReplyToCommentRequest, current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    record = await own_comment(db,current_user,platform,comment_id)
    adapter = await owned_adapter(db,current_user.id,platform)
    reply = await adapter.reply_to_comment(record.platform_comment_id, request.text)
    if not reply.id: raise HTTPException(502,'Provider did not confirm the reply.')
    return {'id':reply.id,'text':reply.text,'created_at':reply.created_at,'platform_data':{}}


@router.delete('/{platform}/{comment_id}')
async def delete_comment(platform: str, comment_id: str, current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    record = await own_comment(db,current_user,platform,comment_id)
    adapter = await owned_adapter(db,current_user.id,platform)
    if not await adapter.delete_comment(record.platform_comment_id): raise HTTPException(502,'Provider did not confirm deletion.')
    await db.delete(record); await db.commit()
    return {'deleted':True}


@router.post('/{platform}/{comment_id}/hide')
async def hide_comment(platform: str, comment_id: str, current_user: User = Depends(get_current_verified_user), db: AsyncSession = Depends(get_db)):
    record = await own_comment(db,current_user,platform,comment_id)
    adapter = await owned_adapter(db,current_user.id,platform)
    if not await adapter.hide_comment(record.platform_comment_id): raise HTTPException(502,'Provider did not confirm hiding.')
    record.is_hidden=True; await db.commit()
    return {'hidden':True}
