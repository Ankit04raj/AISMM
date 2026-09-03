"""Social Accounts API router."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db
from backend.app.db.models import User
from backend.app.api.deps import get_current_user
from backend.app.services.account_service import AccountService
from backend.app.core.schemas.account import (
    ConnectAccountRequest,
    SocialAccountResponse,
    SocialAccountListResponse,
    UpdateAccountRequest,
    DisconnectAccountResponse,
    AccountInsights,
    AccountProfile,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/connect", response_model=SocialAccountResponse, status_code=status.HTTP_201_CREATED)
async def connect_account(
    request: ConnectAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connect a social account for the authenticated user."""
    service = AccountService(db)
    return await service.connect_account(current_user.id, request)


@router.get("", response_model=SocialAccountListResponse)
async def list_accounts(
    platform: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List connected social accounts owned by the authenticated user."""
    service = AccountService(db)
    accounts = await service.get_account_responses(current_user.id, platform)
    return SocialAccountListResponse(accounts=accounts, total=len(accounts))


@router.get("/{account_id}", response_model=SocialAccountResponse)
async def get_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific social account owned by the authenticated user."""
    service = AccountService(db)
    account = await service.get_account(UUID(account_id), current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return service._to_response(account)


@router.patch("/{account_id}", response_model=SocialAccountResponse)
async def update_account(
    account_id: str,
    request: UpdateAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a social account owned by the authenticated user."""
    service = AccountService(db)
    account = await service.update_account(UUID(account_id), current_user.id, request)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.delete("/{account_id}", response_model=DisconnectAccountResponse)
async def disconnect_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a social account owned by the authenticated user."""
    service = AccountService(db)
    return await service.disconnect_account(UUID(account_id), current_user.id)


@router.post("/{account_id}/refresh")
async def refresh_account_token(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Refresh account access token for the authenticated user."""
    service = AccountService(db)
    success = await service.refresh_token(UUID(account_id), current_user.id)
    return {"success": success}


@router.get("/{account_id}/insights", response_model=AccountInsights)
async def get_account_insights(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get account insights for the authenticated user."""
    service = AccountService(db)
    insights = await service.get_account_insights(UUID(account_id), current_user.id)
    if not insights:
        raise HTTPException(status_code=404, detail="Insights not available")
    return insights


@router.get("/{account_id}/profile", response_model=AccountProfile)
async def get_account_profile(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get account profile from platform for the authenticated user."""
    service = AccountService(db)
    profile = await service.get_account_profile(UUID(account_id), current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not available")
    return profile
