import pytest


def test_create_order(test_order):
    assert isinstance(test_order, int) and test_order > 0, "Order ID should be a positive integer"
