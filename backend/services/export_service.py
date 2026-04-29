"""
Calendar export — generates .ics files from itinerary data.
Supports both structured TripItinerary and raw markdown fallback.
"""
import re
from icalendar import Calendar, Event
from datetime import datetime, timedelta


def itinerary_to_ics(itinerary_data: dict, start_date: datetime) -> bytes:
    """
    Convert a structured TripItinerary dict into an ICS calendar file.
    Falls back to markdown parsing if the structure is missing.
    """
    cal = Calendar()
    cal.add("prodid", "-//AI Travel Planner//v2//")
    cal.add("version", "2.0")

    daily_plans = itinerary_data.get("daily_plans", [])

    if daily_plans:
        for day in daily_plans:
            day_num = day.get("day_number", 1)
            current = start_date + timedelta(days=day_num - 1)
            theme = day.get("theme", f"Day {day_num}")

            all_activities = day.get("activities", []) + day.get("meals", [])
            for act in all_activities:
                event = Event()
                event.add("summary", act.get("activity", theme))
                event.add("location", act.get("address") or act.get("location", ""))
                event.add("description", act.get("notes", ""))
                event.add("dtstart", current.date())
                event.add("dtend", current.date())
                event.add("dtstamp", datetime.now())
                cal.add_component(event)
    else:
        # fallback: no structured data
        event = Event()
        event.add("summary", "Travel Itinerary")
        event.add("dtstart", start_date.date())
        event.add("dtend", start_date.date())
        event.add("dtstamp", datetime.now())
        cal.add_component(event)

    return cal.to_ical()


def markdown_to_ics(markdown_text: str, start_date: datetime) -> bytes:
    """
    Parse a markdown itinerary with 'Day N:' headings into calendar events.
    Kept for backward compat with the original single-agent output.
    """
    cal = Calendar()
    cal.add("prodid", "-//AI Travel Planner//v2//")
    cal.add("version", "2.0")

    day_pattern = re.compile(r"Day (\d+)[:\s]+(.*?)(?=Day \d+|$)", re.DOTALL)
    days = day_pattern.findall(markdown_text)

    if not days:
        event = Event()
        event.add("summary", "Travel Itinerary")
        event.add("description", markdown_text[:500])
        event.add("dtstart", start_date.date())
        event.add("dtend", start_date.date())
        event.add("dtstamp", datetime.now())
        cal.add_component(event)
    else:
        for day_num, content in days:
            current = start_date + timedelta(days=int(day_num) - 1)
            event = Event()
            event.add("summary", f"Day {day_num} Itinerary")
            event.add("description", content.strip())
            event.add("dtstart", current.date())
            event.add("dtend", current.date())
            event.add("dtstamp", datetime.now())
            cal.add_component(event)

    return cal.to_ical()
