"""
Tests for service-layer utilities (ICS export, parsers, validators).
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("OPENAI_API_KEY", "sk-test")


def test_markdown_to_ics():
    from backend.services.export_service import markdown_to_ics

    md = "Day 1: Arrive in Paris\nDay 2: Visit Eiffel Tower\nDay 3: Louvre Museum"
    ics = markdown_to_ics(md, datetime(2026, 6, 1))
    assert isinstance(ics, bytes)
    assert b"VCALENDAR" in ics


def test_extract_json_from_text():
    from backend.utils.parsers import extract_json_from_text

    text = 'Here is the result:\n```json\n{"destination": "Paris"}\n```'
    result = extract_json_from_text(text)
    assert result == {"destination": "Paris"}


def test_extract_json_raw():
    from backend.utils.parsers import extract_json_from_text

    result = extract_json_from_text('{"key": "value"}')
    assert result == {"key": "value"}
