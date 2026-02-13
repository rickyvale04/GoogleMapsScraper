"""Tests for scrape_places with mocked Playwright."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import MagicMock, patch, PropertyMock
from scraper.core import scrape_places, Place


def _build_mock_playwright(places_to_return, listing_count=None):
    """Build a fully mocked sync_playwright context manager.

    Returns (mock_pw_cm, mock_page) so tests can inspect the page.
    """
    if listing_count is None:
        listing_count = len(places_to_return)

    mock_page = MagicMock()
    mock_context = MagicMock()
    mock_browser = MagicMock()
    mock_pw = MagicMock()

    # sync_playwright().__enter__() returns the pw object
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_pw)
    mock_cm.__exit__ = MagicMock(return_value=False)

    mock_pw.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    # Locator for search results count during scrolling
    place_locator = MagicMock()
    place_locator.count.return_value = listing_count

    # Build listing mocks
    listing_mocks = []
    for _ in range(listing_count):
        link_mock = MagicMock()
        parent_mock = MagicMock()
        link_mock.locator.return_value = parent_mock
        listing_mocks.append(link_mock)

    place_locator.all.return_value = listing_mocks

    mock_page.locator.return_value = place_locator

    return mock_cm, mock_page, places_to_return


@patch("scraper.core.time.sleep")
@patch("scraper.core.extract_place")
@patch("scraper.core.sync_playwright")
def test_scrape_places_returns_list_of_places(mock_sp, mock_extract, mock_sleep):
    p1 = Place(name="Place A", address="Addr A")
    p2 = Place(name="Place B", address="Addr B")
    mock_cm, mock_page, _ = _build_mock_playwright([p1, p2])
    mock_sp.return_value = mock_cm
    mock_extract.side_effect = [p1, p2]

    result = scrape_places("test query", total=2)
    assert len(result) == 2
    assert result[0].name == "Place A"
    assert result[1].name == "Place B"


@patch("scraper.core.time.sleep")
@patch("scraper.core.extract_place")
@patch("scraper.core.sync_playwright")
def test_scrape_places_deduplicates(mock_sp, mock_extract, mock_sleep):
    p1 = Place(name="Same Place", address="Same Address")
    p2 = Place(name="Same Place", address="Same Address")
    p3 = Place(name="Different", address="Other Address")
    mock_cm, mock_page, _ = _build_mock_playwright([p1, p2, p3], listing_count=3)
    mock_sp.return_value = mock_cm
    mock_extract.side_effect = [p1, p2, p3]

    result = scrape_places("test query", total=10)
    names = [p.name for p in result]
    assert names.count("Same Place") == 1
    assert "Different" in names
    assert len(result) == 2


@patch("scraper.core.time.sleep")
@patch("scraper.core.extract_place")
@patch("scraper.core.sync_playwright")
def test_scrape_places_skips_empty_names(mock_sp, mock_extract, mock_sleep):
    p1 = Place(name="", address="Addr")
    p2 = Place(name="Valid", address="Addr2")
    mock_cm, _, _ = _build_mock_playwright([p1, p2])
    mock_sp.return_value = mock_cm
    mock_extract.side_effect = [p1, p2]

    result = scrape_places("test query", total=5)
    assert len(result) == 1
    assert result[0].name == "Valid"


@patch("scraper.core.time.sleep")
@patch("scraper.core.extract_place")
@patch("scraper.core.sync_playwright")
def test_scrape_places_closes_browser(mock_sp, mock_extract, mock_sleep):
    p1 = Place(name="X", address="Y")
    mock_cm, mock_page, _ = _build_mock_playwright([p1])
    mock_sp.return_value = mock_cm
    mock_extract.return_value = p1

    scrape_places("test", total=1)

    # Verify cleanup happened via context manager __exit__
    mock_cm.__exit__.assert_called_once()
