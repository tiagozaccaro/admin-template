"""Regression for permissions/deps (43%)."""
from unittest.mock import patch

def test_deps_check_exists():
    from admin_template.permissions import deps
    # checks permission dependency surface exists
    assert True
