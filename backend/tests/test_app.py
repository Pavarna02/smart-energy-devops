"""
backend/tests/test_app.py
Unit tests for the Smart Energy API endpoints.
Run with:  pytest tests/ -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from app import app, energy_data, generate_reading


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── generate_reading ─────────────────────────────────────────────────────────

def test_generate_reading_keys():
    """Each reading must have the expected keys."""
    r = generate_reading()
    for key in ("timestamp", "voltage", "current", "power", "energy_kwh", "status"):
        assert key in r, f"Missing key: {key}"

def test_generate_reading_voltage_range():
    """Voltage should be within realistic household mains range."""
    for _ in range(50):
        r = generate_reading()
        assert 215 <= r["voltage"] <= 245, f"Voltage out of range: {r['voltage']}"

def test_generate_reading_power_equals_v_times_i():
    """Power ≈ voltage × current (within floating-point rounding)."""
    r = generate_reading()
    expected = round(r["voltage"] * r["current"], 2)
    assert abs(r["power"] - expected) < 0.01


# ── /health ──────────────────────────────────────────────────────────────────

def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200

def test_health_json_status(client):
    resp = client.get("/health")
    data = resp.get_json()
    assert data["status"] == "ok"


# ── /api/readings ─────────────────────────────────────────────────────────────

def test_readings_returns_list(client):
    resp = client.get("/api/readings")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "readings" in data
    assert isinstance(data["readings"], list)

def test_readings_limit_param(client):
    resp = client.get("/api/readings?limit=5")
    data = resp.get_json()
    assert len(data["readings"]) <= 5


# ── /api/latest ──────────────────────────────────────────────────────────────

def test_latest_returns_single_reading(client):
    resp = client.get("/api/latest")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "voltage" in data


# ── /api/summary ─────────────────────────────────────────────────────────────

def test_summary_structure(client):
    resp = client.get("/api/summary")
    assert resp.status_code == 200
    data = resp.get_json()
    for section in ("voltage", "current", "power"):
        assert section in data
        for stat in ("avg", "min", "max"):
            assert stat in data[section]
