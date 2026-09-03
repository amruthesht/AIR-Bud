"""
Calendar Exporter - Generates iCal (.ics) files and Google Calendar links.
"""
import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event
from dateutil.parser import parse as parse_date
import io


def _parse_event_date(date_str: str, default_year: int = None) -> datetime:
    """Try to parse a date string into a datetime object."""
    if not date_str:
        return None
    try:
        if default_year:
            # If only month/day, prepend year
            dt = parse_date(date_str)
            if dt.year == 1900:  # dateutil default for no year
                dt = dt.replace(year=default_year)
            return dt
        return parse_date(date_str)
    except (ValueError, TypeError):
        return None


def generate_ics(syllabus_data: dict, event_duration_hours: int = 2) -> bytes:
    """
    Generate an iCal (.ics) file from parsed syllabus data.

    Args:
        syllabus_data: Dict with 'key_dates', 'course_info' from syllabus parser
        event_duration_hours: Default duration for calendar events

    Returns:
        Bytes of the .ics file
    """
    cal = Calendar()
    cal.add("prodid", "-//StudyMate//Calendar//EN")
    cal.add("version", "2.0")

    course_info = syllabus_data.get("course_info", {})
    course_name = course_info.get("course_name", course_info.get("course_code", "Course"))

    for event_data in syllabus_data.get("key_dates", []):
        event = Event()
        event_name = event_data.get("event_name", "Event")
        event_type = event_data.get("type", "other")
        description = event_data.get("description", "")
        weight = event_data.get("weight")

        dt_start = _parse_event_date(event_data.get("date"))
        if not dt_start:
            continue

        dt_end = dt_start + timedelta(hours=event_duration_hours)

        event.add("summary", f"[{event_type.upper()}] {event_name}")
        event.add("dtstart", dt_start)
        event.add("dtend", dt_end)

        desc_lines = [f"Course: {course_name}", f"Type: {event_type}"]
        if weight:
            desc_lines.append(f"Weight: {weight}%")
        if description:
            desc_lines.append(f"Details: {description}")
        event.add("description", "\n".join(desc_lines))

        event.add("categories", [event_type.upper()])
        cal.add_component(event)

    return cal.to_ical()


def generate_google_calendar_url(syllabus_data: dict, event_duration_hours: int = 2) -> list:
    """
    Generate Google Calendar add URLs for each syllabus event.

    Returns a list of dicts with event info and the Google Calendar URL.
    """
    course_info = syllabus_data.get("course_info", {})
    course_name = course_info.get("course_name", course_info.get("course_code", "Course"))

    urls = []
    for event_data in syllabus_data.get("key_dates", []):
        dt_start = _parse_event_date(event_data.get("date"))
        if not dt_start:
            continue

        dt_end = dt_start + timedelta(hours=event_duration_hours)

        event_name = event_data.get("event_name", "Event")
        event_type = event_data.get("type", "other")
        description = event_data.get("description", "")
        weight = event_data.get("weight")

        summary = f"[{event_type.upper()}] {event_name} - {course_name}"
        desc = f"Type: {event_type}\nCourse: {course_name}"
        if weight:
            desc += f"\nWeight: {weight}%"
        if description:
            desc += f"\nDetails: {description}"

        start_str = dt_start.strftime("%Y%m%dT%H%M00")
        end_str = dt_end.strftime("%Y%m%dT%H%M00")

        from urllib.parse import quote
        url = (
            f"https://calendar.google.com/calendar/render?action=TEMPLATE"
            f"&text={quote(summary)}"
            f"&dates={start_str}/{end_str}"
            f"&details={quote(desc)}"
        )

        urls.append({
            "event_name": event_name,
            "event_type": event_type,
            "date": event_data.get("date"),
            "description": description,
            "weight": weight,
            "url": url,
        })

    return urls
