"""Pluggable email abstraction with a no-op/log default provider."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    to: str
    subject: str
    body: str
    html: str | None = None


class EmailProvider(Protocol):
    async def send(self, message: EmailMessage) -> None: ...


class NoOpEmailProvider:
    """Default provider: logs the email and discards it (dev-friendly)."""

    async def send(self, message: EmailMessage) -> None:
        logger.info(
            "email.noop",
            extra={
                "to": message.to,
                "subject": message.subject,
                "body_preview": message.body[:200],
            },
        )


_provider: EmailProvider = NoOpEmailProvider()


def set_email_provider(provider: EmailProvider) -> None:
    global _provider
    _provider = provider


def get_email_provider() -> EmailProvider:
    return _provider


async def send_email(message: EmailMessage) -> None:
    await _provider.send(message)


__all__ = [
    "EmailMessage",
    "EmailProvider",
    "NoOpEmailProvider",
    "get_email_provider",
    "send_email",
    "set_email_provider",
]
