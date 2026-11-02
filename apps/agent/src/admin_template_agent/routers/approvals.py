"""Approval endpoints for the agent daemon.

Human approval flow (FR-006 / US3): when a destructive tool needs approval,
the SSE stream emits an `approval_request` event and suspends the tool call
until `POST /approve/{id}` is resolved.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from admin_template_agent.auth import verify_token

router = APIRouter()


@router.post("/approve/{approval_id}")
async def approve(
    approval_id: str,
    body: dict,
    token: Annotated[str | None, Depends(verify_token)],
) -> dict:
    """Resolve a pending destructive-action approval."""
    from admin_template_agent.routers import chat

    approved = bool(body.get("approved", False))
    resolved = False
    # Try to resolve in any active registry
    for reg in list(chat._approvals_by_session.values()):
        if reg.resolve(approval_id, approved):
            resolved = True
            break
    if not resolved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown or expired approval request",
        )
    return {"status": "ok", "approved": approved}


__all__ = ["router"]
