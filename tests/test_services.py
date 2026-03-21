"""
Tests for service layer utilities.
"""
import os
import sys
import pytest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("OPENAI_API_KEY", "sk-test")


def test_markdown_to_ics():
    from services.export_service import markdown_to_ics

    md = "Day 1: Arrive in Paris\nDay 2: Visit Eiffel Tower\nDay 3: Louvre Museum"
    ics = markdown_to_ics(md, datetime(2025, 6, 1))
    assert isinstance(ics, bytes)
    assert b"VCALENDAR" in ics


def test_itinerary_to_ics_structured():
    from services.export_service import itinerary_to_ics

    data = {
        "daily_plans": [
            {
                "day_number": 1,
                "theme": "Arrival",
                "activities": [
                    {"activity": "Check in", "location": "Hotel", "address": "123 Main St"}
                ],
                "meals": [],
            }
        ]
    }
    ics = itinerary_to_ics(data, datetime(2025, 6, 1))
    assert b"Check in" in ics


def test_extract_json_from_text():
    from utils.parsers import extract_json_from_text

    text = 'Here is the result:\n```json\n{"destination": "Paris"}\n```'
    result = extract_json_from_text(text)
    assert result == {"destination": "Paris"}


def test_extract_json_raw():
    from utils.parsers import extract_json_from_text

    result = extract_json_from_text('{"key": "value"}')
    assert result == {"key": "value"}


def test_extract_cost_breakdown():
    from utils.parsers import extract_cost_breakdown

    itinerary = {
        "total_estimated_cost_usd": 500,
        "daily_plans": [
            {
                "day_number": 1,
                "activities": [{"cost_usd": 50}, {"cost_usd": 30}],
                "meals": [{"cost_usd": 20}],
            }
        ],
    }
    breakdown = extract_cost_breakdown(itinerary)
    assert breakdown["Activities"] == 80
    assert breakdown["Food"] == 20
    assert "Accommodation & Other" in breakdown


def test_validate_trip_input():
    from utils.validators import validate_trip_input

    assert validate_trip_input("Paris", 7, 2000) == []
    errors = validate_trip_input("", 0, 50)
    assert len(errors) == 3
