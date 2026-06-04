from __future__ import annotations


def build_itinerary(
    destination_id: int,
    destination_name: str,
    days: int,
    who: str,
    budget_tier: str,
    style: str = "cả hai",
) -> str:
    """Build a full Vinpearl itinerary with room suggestions and cost estimate."""
    try:
        from services.chatbot import (
            _find_vp_room, _find_vp_deal,
            _get_all_dest_rooms, _build_vp_timeline,
        )
        dest_id = int(destination_id)
        days    = max(1, min(int(days), 14))
        room    = _find_vp_room(who, budget_tier, style, dest_id)
        deal    = _find_vp_deal(room, dest_id)
        all_rooms = _get_all_dest_rooms(dest_id)
        return _build_vp_timeline(
            who, style, room, deal, days,
            destination_name, dest_id, all_rooms, budget_tier,
        )
    except Exception as exc:
        return f"Lỗi xây dựng lịch trình: {exc}"
