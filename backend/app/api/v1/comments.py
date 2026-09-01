"""Comments API router."""

from fastapi import APIRouter, HTTPException, Depends
from backend.app.core.platform_adapters import PlatformRegistry
from backend.app.core.schemas.post import ReplyToCommentRequest, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/posts/{platform}/{post_id}")
async def list_comments(platform: str, post_id: str, limit: int = 50):
    """List comments on a platform post."""
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    adapter = PlatformRegistry.get_adapter(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Adapter unavailable: {platform}")

    comments = await adapter.get_comments(post_id, limit=limit)
    return {
        "platform": platform,
        "post_id": post_id,
        "comments": [
            {
                "id": c.id,
                "text": c.text,
                "author_name": c.author_name,
                "author_id": c.author_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "is_hidden": c.is_hidden,
                "platform_data": c.platform_data,
            }
            for c in comments
        ],
    }


@router.post("/{platform}/{comment_id}/reply")
async def reply_to_comment(platform: str, comment_id: str, request: ReplyToCommentRequest):
    """Reply to a comment."""
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    adapter = PlatformRegistry.get_adapter(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Adapter unavailable: {platform}")

    reply = await adapter.reply_to_comment(comment_id, request.text)
    return {
        "id": reply.id,
        "text": reply.text,
        "created_at": reply.created_at.isoformat() if reply.created_at else None,
        "platform_data": reply.platform_data,
    }


@router.delete("/{platform}/{comment_id}")
async def delete_comment(platform: str, comment_id: str):
    """Delete a comment."""
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    adapter = PlatformRegistry.get_adapter(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Adapter unavailable: {platform}")

    success = await adapter.delete_comment(comment_id)
    return {"deleted": success, "comment_id": comment_id}


@router.post("/{platform}/{comment_id}/hide")
async def hide_comment(platform: str, comment_id: str):
    """Hide a comment."""
    if not PlatformRegistry.is_registered(platform):
        raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

    adapter = PlatformRegistry.get_adapter(platform)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Adapter unavailable: {platform}")

    success = await adapter.hide_comment(comment_id)
    return {"hidden": success, "comment_id": comment_id}
