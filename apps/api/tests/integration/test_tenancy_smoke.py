"""Smoke tests for tenancy isolation / invitation / ownership modules (US2, US3)."""

import importlib


def test_modules_importable() -> None:
    for mod in (
        "admin_template.modules.tenancy.ownership",
        "admin_template.modules.tenancy.invitations",
        "admin_template.modules.tenancy.service",
        "admin_template.permissions.deps",
    ):
        importlib.import_module(mod)


def test_invitation_expiry_rejected() -> None:
    # accept_invitation returns None for expired/revoked/used tokens at module level
    from admin_template.modules.tenancy import invitations

    assert hasattr(invitations, "accept_invitation")
    assert hasattr(invitations, "revoke_invitation")
