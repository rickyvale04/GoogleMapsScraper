"""Tests for config.py — verify expected keys and sensible defaults."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config


def test_xpaths_has_expected_keys():
    expected = [
        "name", "address", "website", "phone_number",
        "reviews_count", "reviews_average",
        "info1", "info2", "info3",
        "opens_at", "opens_at2",
        "place_type", "introduction",
    ]
    for key in expected:
        assert key in config.XPATHS, f"Missing XPATHS key: {key}"


def test_user_agents_non_empty():
    assert isinstance(config.USER_AGENTS, list)
    assert len(config.USER_AGENTS) > 0


def test_user_agents_are_strings():
    for ua in config.USER_AGENTS:
        assert isinstance(ua, str)
        assert len(ua) > 10


def test_browser_args_is_list():
    assert isinstance(config.BROWSER_ARGS, list)
    assert len(config.BROWSER_ARGS) > 0


def test_timeouts_are_positive():
    assert config.DEFAULT_PAGE_TIMEOUT > 0
    assert config.NAVIGATION_TIMEOUT > 0
    assert config.PLACE_DETAIL_TIMEOUT > 0
    assert config.PLACE_DETAIL_FALLBACK_TIMEOUT > 0


def test_default_proxy_is_none():
    assert config.DEFAULT_PROXY is None


def test_default_headless_is_true():
    assert config.DEFAULT_HEADLESS is True


def test_retry_counts_positive():
    assert config.EXTRACT_RETRY_COUNT >= 1
    assert config.NAVIGATION_RETRY_COUNT >= 1


def test_server_settings():
    assert config.SERVER_PORT > 0
    assert isinstance(config.SERVER_HOST, str)


def test_maps_start_url():
    assert config.MAPS_START_URL.startswith("https://www.google.com/maps")
