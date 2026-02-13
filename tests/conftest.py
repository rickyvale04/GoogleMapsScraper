"""Shared fixtures for Google Maps Scraper tests."""

import sys
import os
import pytest
from unittest.mock import MagicMock

# Ensure project root is on sys.path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scraper.core import Place
from api.server import app, active_searches


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page object."""
    page = MagicMock()
    # Default: locator().count() returns 0 (element not found)
    page.locator.return_value.count.return_value = 0
    page.locator.return_value.inner_text.return_value = ""
    return page


@pytest.fixture
def sample_place():
    """Return a sample Place with realistic data."""
    return Place(
        name="Test Store",
        address="123 Main St, Toronto, ON",
        website="www.teststore.com",
        phone_number="+1-416-555-0100",
        reviews_count=42,
        reviews_average=4.5,
        store_shopping="Yes",
        in_store_pickup="No",
        store_delivery="Yes",
        place_type="Store",
        opens_at="Opens 9AM",
        introduction="A great test store",
    )


@pytest.fixture
def test_client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    # Clean up active_searches after each test
    active_searches.clear()
