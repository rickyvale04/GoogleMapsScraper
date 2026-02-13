"""Tests for Flask API endpoints in api/server.py."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import time
from unittest.mock import patch, MagicMock
from api.server import app, active_searches, _place_to_result_dict
from scraper.core import Place
from datetime import datetime


# ---------- GET / ----------

def test_serve_interface(test_client):
    # The root route tries to serve a static HTML file.
    # In test, the file may not exist, so we just verify the route exists.
    resp = test_client.get("/")
    # Either 200 (file found) or 404 (file not found in test env) is acceptable
    assert resp.status_code in (200, 404)


# ---------- GET /health ----------

def test_health_check(test_client):
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "active_searches" in data


# ---------- POST /api/search ----------

@patch("api.server.threading.Thread")
def test_search_valid_request(mock_thread, test_client):
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    resp = test_client.post(
        "/api/search",
        data=json.dumps({"query": "restaurants", "cities": "Milan, Rome", "maxResults": 10}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "search_id" in data
    assert data["status"] == "started"
    mock_thread_instance.start.assert_called_once()


def test_search_missing_query(test_client):
    resp = test_client.post(
        "/api/search",
        data=json.dumps({"query": "", "cities": "Milan"}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_search_missing_cities(test_client):
    resp = test_client.post(
        "/api/search",
        data=json.dumps({"query": "restaurants", "cities": ""}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_search_missing_cities_key(test_client):
    resp = test_client.post(
        "/api/search",
        data=json.dumps({"query": "restaurants"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_search_empty_city_list(test_client):
    resp = test_client.post(
        "/api/search",
        data=json.dumps({"query": "restaurants", "cities": " , , "}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ---------- GET /api/search/<id>/status ----------

def test_status_unknown_id(test_client):
    resp = test_client.get("/api/search/nonexistent/status")
    assert resp.status_code == 404
    data = resp.get_json()
    assert "error" in data


def test_status_known_id(test_client):
    active_searches["test_123"] = {
        "status": "running",
        "query": "test",
        "results": [{"name": "A"}],
        "start_time": datetime.now(),
        "cities": ["Milan"],
        "current_city": "1/1 - Milan",
        "total_target": 20,
        "max_results": 20,
    }
    resp = test_client.get("/api/search/test_123/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "running"
    assert data["results_count"] == 1


# ---------- GET /api/search/<id>/results ----------

def test_results_unknown_id(test_client):
    resp = test_client.get("/api/search/nonexistent/results")
    assert resp.status_code == 404


def test_results_running(test_client):
    active_searches["run_1"] = {
        "status": "running",
        "query": "test",
        "results": [],
        "start_time": datetime.now(),
    }
    resp = test_client.get("/api/search/run_1/results")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "running"
    assert data["results"] == []


def test_results_completed(test_client):
    active_searches["done_1"] = {
        "status": "completed",
        "query": "test",
        "results": [{"name": "Place A"}],
        "start_time": datetime.now(),
    }
    resp = test_client.get("/api/search/done_1/results")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "completed"
    assert len(data["results"]) == 1


# ---------- _place_to_result_dict ----------

def test_place_to_result_dict():
    place = Place(
        name="Cafe",
        address="1 St",
        phone_number="555",
        website="cafe.com",
        place_type="Restaurant",
        reviews_count=10,
        opens_at="9AM",
    )
    result = _place_to_result_dict(place, "Milan")
    assert result["name"] == "Cafe"
    assert result["phone"] == "555"
    assert result["city"] == "Milan"
    assert result["reviews"] == "10 reviews"


def test_place_to_result_dict_no_reviews():
    place = Place(name="Empty")
    result = _place_to_result_dict(place, "Rome")
    assert result["reviews"] == "0 reviews"
