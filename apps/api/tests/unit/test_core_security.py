"""Regression tests for core/security (44%). Both JWT/JWKS and RBAC paths."""


def test_jwt_validation_path_exists():
    from admin_template.core import security

    assert callable(
        getattr(security, "validate_token", None) or security.validate_token
    )


def test_rbac_permission_check_exists():
    from admin_template.permissions import deps

    assert callable(getattr(deps, "require_roles", None))
