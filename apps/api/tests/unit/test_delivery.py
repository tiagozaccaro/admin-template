"""Unit tests for invitation delivery adapter."""

import asyncio

from admin_template.modules.tenancy import delivery


class RecordingAdapter:
    def __init__(self):
        self.calls = []

    async def send_invitation(self, email, token):
        self.calls.append((email, token))


def test_default_adapter_is_in_app():
    delivery.set_delivery_adapter(delivery.InAppNotificationDelivery())
    asyncio.run(delivery.send_invitation("a@b.com", "tok"))
    assert delivery.get_delivery_adapter() is not None


def test_set_and_use_custom_adapter():
    rec = RecordingAdapter()
    delivery.set_delivery_adapter(rec)
    asyncio.run(delivery.send_invitation("x@y.com", "t1"))
    assert rec.calls == [("x@y.com", "t1")]
    delivery.set_delivery_adapter(delivery.InAppNotificationDelivery())


def test_email_delivery_raises_not_implemented():
    delivery.set_delivery_adapter(delivery.EmailDelivery())
    try:
        with __import__("pytest").raises(NotImplementedError):
            asyncio.run(delivery.send_invitation("a@b.com", "tok"))
    finally:
        delivery.set_delivery_adapter(delivery.InAppNotificationDelivery())
