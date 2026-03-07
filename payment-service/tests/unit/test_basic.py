"""
Basic tests to verify pytest setup
"""

import pytest


def test_basic_assertion():
    """Test that pytest is working"""
    assert True


def test_basic_math():
    """Test basic math operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6


def test_string_operations():
    """Test string operations"""
    text = "Payment Service"
    assert "Payment" in text
    assert text.startswith("Payment")
    assert text.endswith("Service")


@pytest.mark.unit
def test_with_marker():
    """Test with unit marker"""
    assert "saga" == "saga"
