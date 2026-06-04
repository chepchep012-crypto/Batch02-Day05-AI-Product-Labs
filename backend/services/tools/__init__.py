from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from services.tools.clarify.tool import ask_user
from services.tools.get_destinations.tool import get_destinations
from services.tools.get_rooms.tool import get_rooms
from services.tools.get_promotions.tool import get_promotions
from services.tools.build_itinerary.tool import build_itinerary
from services.tools.submit_booking.tool import submit_booking

# ── Registry: tool name → Python function ────────────────────────────────────
TOOL_FUNCTIONS: dict[str, Any] = {
    "clarify":          ask_user,
    "get_destinations": get_destinations,
    "get_rooms":        get_rooms,
    "get_promotions":   get_promotions,
    "build_itinerary":  build_itinerary,
    "submit_booking":   submit_booking,
}


def load_tool_declarations(path: Path | str | None = None) -> list[dict[str, Any]]:
    """Load tool schemas from YAML file."""
    if path is None:
        path = Path(__file__).parent.parent / "artifacts" / "tools.yaml"
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))["tools"]


def to_openai_tools(declarations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert YAML tool declarations → OpenAI-compatible function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": item["name"],
                "description": item.get("description", ""),
                "parameters": item.get("parameters", {"type": "object", "properties": {}}),
            },
        }
        for item in declarations
    ]
