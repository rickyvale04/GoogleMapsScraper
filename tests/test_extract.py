"""Tests for extract_text, extract_place, and _do_extract_place."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch
from scraper.core import extract_text, extract_place, _do_extract_place, Place
from config import XPATHS


# ---------- extract_text ----------

def test_extract_text_returns_text_when_element_exists(mock_page):
    mock_page.locator.return_value.count.return_value = 1
    mock_page.locator.return_value.inner_text.return_value = "Hello"
    result = extract_text(mock_page, "//some/xpath")
    assert result == "Hello"


def test_extract_text_returns_empty_when_element_not_found(mock_page):
    mock_page.locator.return_value.count.return_value = 0
    result = extract_text(mock_page, "//missing/xpath")
    assert result == ""


def test_extract_text_returns_empty_on_exception(mock_page):
    mock_page.locator.side_effect = Exception("boom")
    result = extract_text(mock_page, "//bad/xpath")
    assert result == ""


# ---------- _do_extract_place ----------

def _make_page_with_texts(mapping: dict):
    """Helper: create a mock page that returns specific text for specific xpaths."""
    page = MagicMock()

    def locator_side_effect(xpath):
        loc = MagicMock()
        if xpath in mapping:
            loc.count.return_value = 1
            loc.inner_text.return_value = mapping[xpath]
        else:
            loc.count.return_value = 0
            loc.inner_text.return_value = ""
        return loc

    page.locator.side_effect = locator_side_effect
    return page


def test_do_extract_place_populates_all_fields():
    mapping = {
        XPATHS["name"]: "Coffee Shop",
        XPATHS["address"]: "456 Elm St",
        XPATHS["website"]: "coffeeshop.com",
        XPATHS["phone_number"]: "+1-555-1234",
        XPATHS["place_type"]: "Cafe",
        XPATHS["introduction"]: "Great coffee",
        XPATHS["reviews_count"]: "(123)",
        XPATHS["reviews_average"]: "4,5",
        XPATHS["opens_at"]: "Open\u22c5Opens 8\u202fAM",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.name == "Coffee Shop"
    assert place.address == "456 Elm St"
    assert place.website == "coffeeshop.com"
    assert place.phone_number == "+1-555-1234"
    assert place.place_type == "Cafe"
    assert place.introduction == "Great coffee"
    assert place.reviews_count == 123
    assert place.reviews_average == 4.5
    assert place.opens_at == "Opens 8AM"


def test_do_extract_place_empty_page():
    page = _make_page_with_texts({})
    place = _do_extract_place(page)
    assert place.name == ""
    assert place.address == ""
    assert place.reviews_count is None
    assert place.reviews_average is None
    assert place.introduction == "None Found"


def test_do_extract_place_malformed_reviews_count():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["reviews_count"]: "not-a-number",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.name == "Shop"
    assert place.reviews_count is None  # parsing fails gracefully


def test_do_extract_place_reviews_count_with_commas():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["reviews_count"]: "(1,234)",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.reviews_count == 1234


def test_do_extract_place_store_info_shopping():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["info1"]: "Services\u00b7In-store shopping",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.store_shopping == "Yes"


def test_do_extract_place_store_info_pickup():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["info2"]: "Services\u00b7In-store pickup",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.in_store_pickup == "Yes"


def test_do_extract_place_store_info_delivery():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["info3"]: "Services\u00b7Delivery available",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.store_delivery == "Yes"


def test_do_extract_place_opens_at_no_separator():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["opens_at"]: "Open 24 hours",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.opens_at == "Open 24 hours"


def test_do_extract_place_opens_at_fallback():
    mapping = {
        XPATHS["name"]: "Shop",
        XPATHS["opens_at2"]: "Closed\u22c5Opens 10\u202fAM",
    }
    page = _make_page_with_texts(mapping)
    place = _do_extract_place(page)
    assert place.opens_at == "Opens 10AM"


# ---------- extract_place (with retry) ----------

@patch("scraper.core.time.sleep")
def test_extract_place_returns_on_first_success(mock_sleep):
    mapping = {XPATHS["name"]: "Good Place"}
    page = _make_page_with_texts(mapping)
    place = extract_place(page)
    assert place.name == "Good Place"
    mock_sleep.assert_not_called()


@patch("scraper.core.time.sleep")
@patch("scraper.core._do_extract_place")
def test_extract_place_retries_on_empty_name(mock_do_extract, mock_sleep):
    empty_place = Place()
    good_place = Place(name="Retry Success")
    mock_do_extract.side_effect = [empty_place, good_place]

    page = MagicMock()
    place = extract_place(page)
    assert place.name == "Retry Success"
    assert mock_do_extract.call_count == 2


@patch("scraper.core.time.sleep")
@patch("scraper.core._do_extract_place")
def test_extract_place_clicks_listing_on_retry(mock_do_extract, mock_sleep):
    empty_place = Place()
    good_place = Place(name="After Click")
    mock_do_extract.side_effect = [empty_place, good_place]

    page = MagicMock()
    listing = MagicMock()
    place = extract_place(page, listing=listing)
    assert place.name == "After Click"
    listing.click.assert_called_once()


@patch("scraper.core.time.sleep")
@patch("scraper.core._do_extract_place")
def test_extract_place_returns_empty_after_all_retries(mock_do_extract, mock_sleep):
    empty_place = Place()
    mock_do_extract.return_value = empty_place

    page = MagicMock()
    place = extract_place(page)
    assert place.name == ""
    # 1 initial + EXTRACT_RETRY_COUNT retries
    from config import EXTRACT_RETRY_COUNT
    assert mock_do_extract.call_count == 1 + EXTRACT_RETRY_COUNT
