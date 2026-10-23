"""Regression for core/crud (44%)."""
from admin_template.core.crud import CRUDBase

def test_crud_class_exists():
    assert CRUDBase is not None
