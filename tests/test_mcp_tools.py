import math
import pytest

from mcp_server.tools.optimizer import (
    _haversine_km,
    _nearest_neighbour,
    _tour_length_km,
    _two_opt,
    optimize_day_route,
)
from mcp_server.tools.scorer import (
    _coherence_score,
    _feasibility_score,
    _budget_score,
    _diversity_score,
    _pacing_score,
    _opening_hours_score,
    score_itinerary,
)


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------

def test_haversine_same_point():
    assert _haversine_km((28.6, 77.2), (28.6, 77.2)) == pytest.approx(0.0, abs=1e-6)


def test_haversine_known_distance():
    # Delhi (28.6139, 77.2090) to Mumbai (19.0760, 72.8777) ≈ 1148 km
    d = _haversine_km((28.6139, 77.2090), (19.0760, 72.8777))
    assert 1100 < d < 1200


def test_haversine_symmetric():
    a, b = (28.6, 77.2), (19.1, 72.9)
    assert _haversine_km(a, b) == pytest.approx(_haversine_km(b, a), rel=1e-9)


# ---------------------------------------------------------------------------
# Nearest-neighbour
# ---------------------------------------------------------------------------

def test_nearest_neighbour_visits_all():
    coords = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]
    order = _nearest_neighbour(coords, start=0)
    assert sorted(order) == [0, 1, 2, 3]


def test_nearest_neighbour_starts_at_index():
    coords = [(0.0, 0.0), (10.0, 0.0), (0.1, 0.0)]
    order = _nearest_neighbour(coords, start=1)
    assert order[0] == 1


def test_nearest_neighbour_single_stop():
    order = _nearest_neighbour([(0.0, 0.0)])
    assert order == [0]


# ---------------------------------------------------------------------------
# Tour length
# ---------------------------------------------------------------------------

def test_tour_length_collinear():
    coords = [(0.0, 0.0), (0.0, 1.0), (0.0, 2.0)]
    order = [0, 1, 2]
    total = _tour_length_km(order, coords)
    assert total == pytest.approx(
        _haversine_km(coords[0], coords[1]) + _haversine_km(coords[1], coords[2]),
        rel=1e-6,
    )


# ---------------------------------------------------------------------------
# 2-opt
# ---------------------------------------------------------------------------

def test_two_opt_does_not_increase_length():
    coords = [(0.0, 0.0), (0.0, 10.0), (10.0, 10.0), (10.0, 0.0), (5.0, 5.0)]
    order = [0, 2, 1, 3, 4]
    before = _tour_length_km(order, coords)
    after_order = _two_opt(order, coords)
    after = _tour_length_km(after_order, coords)
    assert after <= before + 1e-6


def test_two_opt_returns_same_stops():
    coords = [(0.0, i * 0.5) for i in range(5)]
    order = [0, 4, 1, 3, 2]
    result = _two_opt(order, coords)
    assert sorted(result) == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# optimize_day_route
# ---------------------------------------------------------------------------

def test_optimize_day_route_single_stop():
    stops = [{"name": "A", "latitude": 0.0, "longitude": 0.0}]
    result = optimize_day_route(stops)
    assert result["total_distance_km"] == 0.0


def test_optimize_day_route_returns_all_stops():
    stops = [
        {"name": "A", "latitude": 28.6, "longitude": 77.2},
        {"name": "B", "latitude": 28.7, "longitude": 77.1},
        {"name": "C", "latitude": 28.5, "longitude": 77.3},
    ]
    result = optimize_day_route(stops)
    assert len(result["ordered"]) == 3
    assert len(result["legs"]) == 2


def test_optimize_day_route_missing_coords():
    stops = [{"name": "A"}, {"name": "B", "latitude": 1.0, "longitude": 1.0}]
    result = optimize_day_route(stops)
    assert "error" in result


# ---------------------------------------------------------------------------
# Scorer: coherence
# ---------------------------------------------------------------------------

def test_coherence_nearby_stops_high_score():
    # Stops within ~1 km of each other should score near 100
    day = {"activities": [
        {"latitude": 28.6, "longitude": 77.2},
        {"latitude": 28.601, "longitude": 77.201},
    ]}
    score, _ = _coherence_score([day])
    assert score > 90


def test_coherence_distant_stops_lower_score():
    day = {"activities": [
        {"latitude": 28.6, "longitude": 77.2},
        {"latitude": 19.1, "longitude": 72.9},
    ]}
    score, _ = _coherence_score([day])
    assert score < 50


# ---------------------------------------------------------------------------
# Scorer: feasibility
# ---------------------------------------------------------------------------

def test_feasibility_all_ok():
    day = {"activities": [{"duration_minutes": 60}] * 8}  # 480 min < 840 (14h)
    score, meta = _feasibility_score([day])
    assert score == 100.0
    assert meta["flagged_days"] == 0


def test_feasibility_overloaded_day():
    day = {"activities": [{"duration_minutes": 120}] * 8}  # 960 min > 840
    score, meta = _feasibility_score([day])
    assert score == 0.0
    assert meta["flagged_days"] == 1


# ---------------------------------------------------------------------------
# Scorer: budget
# ---------------------------------------------------------------------------

def test_budget_on_target():
    score, _ = _budget_score(1000.0, 1000.0)
    assert score == pytest.approx(100.0)


def test_budget_over_target():
    score, _ = _budget_score(2000.0, 1000.0)
    assert score < 100.0


def test_budget_no_target():
    score, meta = _budget_score(500.0, 0.0)
    assert score == 50.0


# ---------------------------------------------------------------------------
# Scorer: diversity
# ---------------------------------------------------------------------------

def test_diversity_all_same_kind():
    days = [{"activities": [{"kind": "temple"}, {"kind": "temple"}]}]
    score, _ = _diversity_score(days)
    assert score == 0.0


def test_diversity_many_kinds():
    days = [{"activities": [
        {"kind": "temple"}, {"kind": "beach"}, {"kind": "food"}, {"kind": "hike"},
    ]}]
    score, _ = _diversity_score(days)
    assert score > 80


# ---------------------------------------------------------------------------
# Scorer: pacing
# ---------------------------------------------------------------------------

def test_pacing_uniform():
    days = [{"activities": [{}] * 3}, {"activities": [{}] * 3}]
    score, _ = _pacing_score(days)
    assert score == pytest.approx(100.0)


def test_pacing_uneven():
    days = [{"activities": [{}]}, {"activities": [{}] * 10}]
    score, _ = _pacing_score(days)
    assert score < 100.0


# ---------------------------------------------------------------------------
# Scorer: opening hours
# ---------------------------------------------------------------------------

def test_opening_hours_all_present():
    days = [{"activities": [{"opening_hours": "9am-5pm"}, {"hours": "8am-6pm"}]}]
    score, _ = _opening_hours_score(days)
    assert score == 100.0


def test_opening_hours_none():
    days = [{"activities": [{"name": "A"}, {"name": "B"}]}]
    score, _ = _opening_hours_score(days)
    assert score == 0.0


# ---------------------------------------------------------------------------
# Full score_itinerary
# ---------------------------------------------------------------------------

def test_score_itinerary_returns_all_keys():
    itinerary = {
        "total_budget_usd": 1000,
        "total_estimated_cost_usd": 900,
        "daily_plans": [
            {"activities": [
                {"kind": "beach", "latitude": 15.3, "longitude": 73.9, "duration_minutes": 90},
                {"kind": "food", "latitude": 15.31, "longitude": 73.91, "duration_minutes": 60},
            ]}
        ],
    }
    result = score_itinerary(itinerary)
    assert "overall_score" in result
    assert "verdict" in result
    assert "criteria" in result
    assert set(result["criteria"].keys()) == {
        "coherence", "feasibility", "budget", "diversity", "pacing", "opening_hours"
    }


def test_score_itinerary_empty_plans():
    result = score_itinerary({"daily_plans": [], "total_budget_usd": 1000, "total_estimated_cost_usd": 0})
    assert result["overall_score"] >= 0
