"""IQC Support Agent — Claude via OpenRouter, with Notion tools."""

import json
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from notion_tools import create_note, create_meeting, search_notes, list_recent_pages

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-opus-4")

SYSTEM_PROMPT = f"""You are IQC Support, an AI assistant for the International Quant Competition team.
Today's date is {datetime.now().strftime('%Y-%m-%d')}.

You help the team by:
- Creating and organizing meeting notes in Notion
- Scheduling and recording meetings in Notion
- Searching existing notes and pages
- Answering questions about the competition

When a user asks you to create a note or meeting, always use the provided tools.
Be concise and professional. After completing a Notion action, confirm what was done and share the link."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a new note page in Notion with a title and content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the note"},
                    "content": {"type": "string", "description": "Body content of the note"},
                },
                "required": ["title", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_meeting",
            "description": "Schedule a meeting and record it in Notion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Meeting title/topic"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time": {"type": "string", "description": "Time in HH:MM 24h format"},
                    "attendees": {"type": "string", "description": "Comma-separated list of attendees"},
                    "agenda": {"type": "string", "description": "Meeting agenda or description"},
                },
                "required": ["title", "date", "time", "attendees", "agenda"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "Search Notion pages by keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword or phrase"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_recent_pages",
            "description": "List the most recently edited pages in Notion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of pages to return (default 5)"},
                },
                "required": [],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "create_note": create_note,
    "create_meeting": create_meeting,
    "search_notes": search_notes,
    "list_recent_pages": list_recent_pages,
}


def run_agent(user_message: str) -> str:
    """Run the IQC Support agent for a given user message. Returns the final text response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            tools=TOOLS,
            messages=messages,
        )

        msg = response.choices[0].message
        tool_calls = msg.tool_calls

        # No tool calls — return final text
        if not tool_calls:
            return msg.content or "(No response)"

        # Append assistant turn
        messages.append(msg)

        # Execute each tool and append results
        for tool_call in tool_calls:
            func = TOOL_FUNCTIONS.get(tool_call.function.name)
            if func:
                try:
                    args = json.loads(tool_call.function.arguments)
                    result = func(**args)
                except Exception as e:
                    result = f"Error running {tool_call.function.name}: {e}"
            else:
                result = f"Unknown tool: {tool_call.function.name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
