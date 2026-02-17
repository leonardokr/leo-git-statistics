"""Webhook registration and management endpoints."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl

from api.deps.auth import verify_api_key
from api.middleware.rate_limiter import DEFAULT_LIMIT, limiter
from api.models.requests import validated_username
from src.db.webhooks import webhook_store

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users/{username}/webhooks",
    tags=["Webhooks"],
    dependencies=[Depends(verify_api_key)],
)


class WebhookCreateRequest(BaseModel):
    """Request body for registering a new webhook."""

    url: HttpUrl
    conditions: Dict[str, Any] = Field(
        ...,
        description="Trigger conditions. Supported keys: stars_threshold (int), "
                    "streak_broken (bool), contributions_record (bool).",
    )


class WebhookResponse(BaseModel):
    """Response model for a single webhook."""

    id: str
    username: str
    url: str
    conditions: Dict[str, Any]
    created_at: Optional[str] = None


@router.post(
    "",
    summary="Register a webhook",
    response_model=WebhookResponse,
    status_code=201,
)
@limiter.limit(DEFAULT_LIMIT)
async def create_webhook(
    request: Request,
    body: WebhookCreateRequest,
    username: str = Depends(validated_username),
) -> dict:
    """Register a callback URL to be notified when statistics change significantly."""
    record = webhook_store.create(username, str(body.url), body.conditions)
    return record


@router.get(
    "",
    summary="List webhooks",
    response_model=List[WebhookResponse],
)
@limiter.limit(DEFAULT_LIMIT)
async def list_webhooks(
    request: Request,
    username: str = Depends(validated_username),
) -> list:
    """List all active webhooks for a user."""
    return webhook_store.list_by_user(username)


@router.delete(
    "/{webhook_id}",
    summary="Delete a webhook",
    status_code=204,
)
@limiter.limit(DEFAULT_LIMIT)
async def delete_webhook(
    request: Request,
    webhook_id: str,
    username: str = Depends(validated_username),
) -> None:
    """Remove a webhook registration."""
    hook = webhook_store.get(webhook_id)
    if hook is None or hook["username"] != username.lower():
        raise HTTPException(status_code=404, detail="Webhook not found")
    webhook_store.delete(webhook_id)
