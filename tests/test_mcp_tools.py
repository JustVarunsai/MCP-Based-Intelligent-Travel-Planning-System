import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools.optimizer import (
    _haversine_km, _nearest_neighbour, _tour_length_km, _two_opt,
    optimize_day_route,
)
from mcp_server.tools.scorer import (
    _coherence_score, _feasibility_score, _budget_score,
    _diversity_score, _pacing_score, _opening_hours_score,
    score_itinerary,
)


def test_haversine_paris_london():
    paris = (48.8566, 2.3522)
    london = (51.5074, -0.1278)
    d = _haversine_km(paris, london)
    assert 330 < d < 360, f"expected ~344 km, got {d:.1f}"


def test_haversine_zero_distance():
    p = (10.0, 20.0)
    assert _haversine_km(p, p) < 1e-6


def test_nearest_neighbour_orders_chain():
    coords = [(0, 0), (0, 1), (0, 2), (0, 3)]
    order = _nearest_neighbour(coords, start=0)
    assert order == [0, 1, 2, 3]


def test_two_opt_does_not_increase_tour():
    coords = [(0, 0), (0, 5), (1, 0), (1, 5)]
    initial = [0, 1, 2, 3]
    refined = _two_opt(initial, coords)
    assert _tour_length_km(refined, coords) <= _tour_length_km(initial, coords) + 1e-9


def test_optimize_day_route_paris():
    stops = [
        {"name": "Louvre", "latitude": 48.8606, "longitude": 2.3376},
        {"name": "Notre Dame", "latitude": 48.8530, "longitude": 2.3499},
        {"name": "Eiffel Tower", "latitude": 48.8584, "longitude": 2.2945},
        {"name": "Arc de Triomphe", "latitude": 48.8738, "longitude": 2.2950},
    ]
    fn = optimize_day_route.fn if hasattr(optimize_day_route, "fn") else optimize_day_route
    result = fn(stops)
    assert "ordered" in result
    assert len(result["ordered"]) == 4
    assert result["total_distance_km"] < 15
    names_in = {s["name"] for s in stops}
    names_out = {s["name"] for s in result["ordered"]}
    assert names_in == names_out


def test_optimize_day_route_handles_too_few():
    fn = optimize_day_route.fn if hasattr(optimize_day_route, "fn") else optimize_day_route
    result = fn([{"name": "alone", "latitude": 0, "longitude": 0}])
    assert result["total_distance_km"] == 0.0


def test_optimize_day_route_handles_bad_input():
    fn = optimize_day_route.fn if hasattr(optimize_day_route, "fn") else optimize_day_route
    result = fn([{"name": "x"}, {"name": "y"}])
    assert "error" in result


def test_coherence_perfect_when_all_same_point():
    daily = [{"activities": [
        {"latitude": 0, "longitude": 0},
        {"latitude": 0, "longitude": 0},
    ]}]
    score, _meta = _coherence_score(daily)
    assert score == 100.0


def test_coherence_drops_with_distance():
    near = [{"activities": [
        {"latitude": 0, "longitude": 0},
        {"latitude": 0, "longitude": 0.009},
    ]}]
    far = [{"activities": [
        {"latitude": 0, "longitude": 0},
        {"latitude": 0, "longitude": 0.45},
    ]}]
    s_near, _ = _coherence_score(near)
    s_far, _ = _coherence_score(far)
    assert s_near > s_far


def test_feasibility_perfect_when_all_days_fit():
    daily = [{"activities": [
        {"duration_minutes": 120}, {"duration_minutes": 60},
    ]}]
    score, meta = _feasibility_score(daily)
    assert score == 100.0
    assert meta["flagged_days"] == 0


def test_feasibility_flags_overstuffed_day():
    daily = [{"activities": [{"duration_minutes": 60} for _ in range(20)]}]
    score, meta = _feasibility_score(daily, waking_hours=14)
    assert score == 0.0
    assert meta["flagged_days"] == 1


def test_budget_perfect_when_within_budget():
    score, _ = _budget_score(estimated_cost=900, target_budget=1000)
    assert score == 100.0


def test_budget_penalises_overrun_quadratically():
    on = _budget_score(estimated_cost=1000, target_budget=1000)[0]
    over10 = _budget_score(estimated_cost=1100, target_budget=1000)[0]
    over30 = _budget_score(estimated_cost=1300, target_budget=1000)[0]
    assert on > over10 > over30
    assert (100 - over30) / max(1, (100 - over10)) > 4


def test_diversity_higher_with_more_categories():
    same = [{"activities": [{"kind": "museum"} for _ in range(4)]}]
    mixed = [{"activities": [
        {"kind": "museum"}, {"kind": "park"},
        {"kind": "food"}, {"kind": "shop"},
    ]}]
    s_same, _ = _diversity_score(same)
    s_mixed, _ = _diversity_score(mixed)
    assert s_mixed > s_same


def test_pacing_higher_when_evenly_distributed():
    even = [{"activities": [1, 2, 3]} for _ in range(3)]
    uneven = [{"activities": [1] * 10}, {"activities": []}, {"activities": [1]}]
    s_even, _ = _pacing_score(even)
    s_uneven, _ = _pacing_score(uneven)
    assert s_even > s_uneven


def test_opening_hours_score_percentage():
    daily = [{"activities": [
        {"opening_hours": "10-18"}, {"opening_hours": "9-17"},
        {}, {},
    ]}]
    score, meta = _opening_hours_score(daily)
    assert score == 50.0
    assert meta["with_hours"] == 2


def test_score_itinerary_smoke_full_object():
    sample = {
        "total_budget_usd": 1500,
        "total_estimated_cost_usd": 1300,
        "daily_plans": [
            {
                "day_number": 1, "theme": "sights",
                "activities": [
                    {"kind": "museum", "duration_minutes": 120,
                     "latitude": 48.86, "longitude": 2.34, "opening_hours": "10-18"},
                    {"kind": "park", "duration_minutes": 90,
                     "latitude": 48.87, "longitude": 2.30},
                    {"kind": "food", "duration_minutes": 60,
                     "latitude": 48.87, "longitude": 2.30},
                ],
            },
            {
                "day_number": 2, "theme": "more sights",
                "activities": [
                    {"kind": "museum", "duration_minutes": 90, "latitude": 48.85, "longitude": 2.34},
                    {"kind": "shop", "duration_minutes": 90, "latitude": 48.86, "longitude": 2.34},
                ],
            },
        ],
    }
    fn = score_itinerary.fn if hasattr(score_itinerary, "fn") else score_itinerary
    result = fn(sample)
    assert "overall_score" in result
    assert 0 <= result["overall_score"] <= 100
    assert result["verdict"] in ("excellent", "good", "ok", "needs revision")
    assert set(result["criteria"].keys()) == {
        "coherence", "feasibility", "budget", "diversity", "pacing", "opening_hours",
    }
    for name, c in result["criteria"].items():
        assert 0 <= c["score"] <= 100, f"{name} out of range: {c}"


def test_score_itinerary_handles_empty():
    fn = score_itinerary.fn if hasattr(score_itinerary, "fn") else score_itinerary
    result = fn({"daily_plans": []})
    assert "overall_score" in result
