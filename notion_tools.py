"""Notion tool functions for IQC Support Agent."""

import os
from datetime import datetime
from notion_client import Client

notion = Client(auth=os.getenv("NOTION_API_KEY"))
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")


def _text_block(content: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": content}}]
        },
    }


def create_note(title: str, content: str) -> str:
    """Create a new note page in Notion under the IQC parent page."""
    page = notion.pages.create(
        parent={"page_id": PARENT_PAGE_ID},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        children=[_text_block(content)],
    )
    url = page.get("url", "")
    return f"Note created: '{title}'\nURL: {url}"


def create_meeting(
    title: str,
    date: str,
    time: str,
    attendees: str,
    agenda: str,
) -> str:
    """Create a meeting record in Notion. date format: YYYY-MM-DD, time: HH:MM (24h)."""
    content_lines = [
        f"Date: {date} {time}",
        f"Attendees: {attendees}",
        "",
        "Agenda:",
        agenda,
    ]
    children = [_text_block(line) for line in content_lines]

    page = notion.pages.create(
        parent={"page_id": PARENT_PAGE_ID},
        properties={
            "title": {
                "title": [{"type": "text", "text": {"content": f"[Meeting] {title}"}}]
            }
        },
        children=children,
    )
    url = page.get("url", "")
    return f"Meeting scheduled: '{title}' on {date} at {time}\nAttendees: {attendees}\nURL: {url}"


def search_notes(query: str) -> str:
    """Search Notion pages by keyword."""
    results = notion.search(query=query, filter={"property": "object", "value": "page"})
    pages = results.get("results", [])
    if not pages:
        return f"No pages found for query: '{query}'"

    lines = [f"Found {len(pages)} result(s) for '{query}':"]
    for p in pages[:5]:
        props = p.get("properties", {})
        title_prop = props.get("title", props.get("Name", {}))
        rich_text = title_prop.get("title", title_prop.get("rich_text", []))
        title = rich_text[0]["text"]["content"] if rich_text else "(untitled)"
        url = p.get("url", "")
        lines.append(f"• {title} — {url}")
    return "\n".join(lines)


def list_recent_pages(limit: int = 5) -> str:
    """List the most recently edited Notion pages."""
    results = notion.search(
        query="",
        filter={"property": "object", "value": "page"},
        sort={"direction": "descending", "timestamp": "last_edited_time"},
    )
    pages = results.get("results", [])[:limit]
    if not pages:
        return "No pages found."

    lines = ["Recent Notion pages:"]
    for p in pages:
        props = p.get("properties", {})
        title_prop = props.get("title", props.get("Name", {}))
        rich_text = title_prop.get("title", title_prop.get("rich_text", []))
        title = rich_text[0]["text"]["content"] if rich_text else "(untitled)"
        edited = p.get("last_edited_time", "")[:10]
        url = p.get("url", "")
        lines.append(f"• [{edited}] {title} — {url}")
    return "\n".join(lines)
