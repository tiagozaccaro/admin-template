"""Invitation delivery adapter (pluggable)."""

from __future__ import annotations

from typing import Protocol


class DeliveryAdapter(Protocol):
    async def send_invitation(self, email: str, token: str) -> None: ...


class InAppNotificationDelivery:
    async def send_invitation(self, email: str, token: str) -> None:
        # Default: no external delivery; in-app notifications handled elsewhere
        pass


class EmailDelivery:
    async def send_invitation(self, email: str, token: str) -> None:
        # Placeholder for optional email adapter
        raise NotImplementedError("Email delivery not configured")


_default_adapter = InAppNotificationDelivery()


def get_delivery_adapter() -> DeliveryAdapter:
    return _default_adapter


def set_delivery_adapter(adapter: DeliveryAdapter) -> None:
    global _default_adapter
    _default_adapter = adapter


async def send_invitation(email: str, token: str) -> None:
    adapter = get_delivery_adapter()
    await adapter.send_invitation(email, token)


__all__ = [
    "DeliveryAdapter",
    "EmailDelivery",
    "InAppNotificationDelivery",
    "get_delivery_adapter",
    "send_invitation",
    "set_delivery_adapter",
]
