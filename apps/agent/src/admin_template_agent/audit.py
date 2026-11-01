"""Audit logging for the agent daemon.

Every tool invocation is recorded locally as a JSON-lines file for offline
debugging AND pushed to the core API so the web audit page reflects live
state (FR-007 / SC-004). The API push is best-effort: if the API is
unreachable the local file remains the source of truth and the push is
retried on the next call.
"""

from __future__ import annotations

import logging
import os
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx

from admin_template_agent.config import config

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_pending: dict[str, dict] = {}


def _api_url() -> str | None:
    base = (config.api_url or "").strip()
    if not base:
        return None
    return base.rstrip("/") + "/api/v1/agents/audit"


def _push(entry: dict, path: str | None = None) -> str | None:
    """POST an audit entry to the core API.

    Returns the API-assigned id on success, or None when the API is not
    configured or unreachable.
    """
    url = _api_url()
    if not url or not config.api_token:
        return None
    headers = {"Authorization": f"Bearer {config.api_token}"}
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.post(url, json=entry, headers=headers)
        if resp.status_code >= 400:
            logger.warning(
                "Audit push to %s failed (%s): %s",
                url,
                resp.status_code,
                resp.text[:200],
            )
            return None
        return resp.json().get("id")
    except Exception:
        logger.debug("Audit push to %s failed", url, exc_info=True)
        return None


def _update(audit_id: str, status: str, result_summary: str | None = None) -> bool:
    """PATCH an audit entry's status on the core API."""
    base = (config.api_url or "").strip()
    if not base or not config.api_token:
        return False
    url = base.rstrip("/") + f"/api/v1/agents/audit/{audit_id}"
    headers = {"Authorization": f"Bearer {config.api_token}"}
    payload = {"status": status}
    if result_summary is not None:
        payload["result_summary"] = result_summary
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.patch(url, json=payload, headers=headers)
        return resp.status_code == 200
    except Exception:
        logger.debug("Audit update to %s failed", url, exc_info=True)
        return False


def log_audit(entry: dict, path: str = "audit.log") -> str:
    """Record a tool invocation locally and push it to the core API.

    Returns the audit id: the API-assigned id when the push succeeds, else a
    locally-generated UUID so callers can later update the status.
    """
    record = {"timestamp": datetime.now(UTC).isoformat(), **entry}
    audit_id = str(uuid.uuid4())
    record["id"] = audit_id

    # Local file is the always-on record.
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with Path(path).open("a") as f:
            f.write(__import__("json").dumps(record) + "\n")
    except OSError:
        logger.warning("Could not write local audit log at %s", path)

    # Push to the core API (best-effort, non-blocking).
    api_id = _push(record, path)
    if api_id:
        record["api_id"] = api_id
        return api_id

    with _lock:
        _pending[audit_id] = record
    return audit_id


def update_audit_status(
    audit_id: str,
    status: str,
    result_summary: str | None = None,
    path: str = "audit.log",
) -> bool:
    """Update the status of a previously-recorded audit entry.

    Tries the core API first; if the entry was never pushed (no API), falls
    back to rewriting the local JSON-lines file.
    """
    if _update(audit_id, status, result_summary):
        return True

    # Local fallback: rewrite the matching record in the JSON-lines file.
    try:
        p = Path(path)
        if not p.exists():
            return False
        updated = False
        lines = p.read_text(encoding="utf-8").splitlines()
        with p.open("w") as f:
            for line in lines:
                try:
                    rec = __import__("json").loads(line)
                except Exception:
                    f.write(line + "\n")
                    continue
                if rec.get("id") == audit_id or rec.get("api_id") == audit_id:
                    rec["status"] = status
                    if result_summary is not None:
                        rec["result_summary"] = result_summary
                    f.write(__import__("json").dumps(rec) + "\n")
                    updated = True
                else:
                    f.write(line + "\n")
        return updated
    except OSError:
        return False


__all__ = ["log_audit", "update_audit_status"]