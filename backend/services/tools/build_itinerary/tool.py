from __future__ import annotations


_VALID_WHO    = {"solo", "couple", "family", "group"}
_VALID_BUDGET = {"thấp", "trung", "cao"}


def build_itinerary(
    destination_id: int,
    destination_name: str,
    days: int,
    who: str,
    budget_tier: str,
    style: str = "cả hai",
) -> str:
    """Build a full Vinpearl itinerary with room suggestions and cost estimate."""
    # Guard: refuse if required fields were not confirmed by user
    if not days or int(days) < 1:
        return (
            "❌ TOOL_ERROR: `days` chưa được user xác nhận. "
            "Hãy dùng tool `clarify` để hỏi: 'Chuyến đi bao nhiêu ngày?' TRƯỚC khi gọi build_itinerary."
        )
    if not who or who not in _VALID_WHO:
        return (
            "❌ TOOL_ERROR: `who` chưa được user xác nhận. "
            "Hãy dùng tool `clarify` để hỏi: "
            "'Bạn đi với ai?' với options [Cặp đôi, Gia đình, Nhóm bạn, Một mình] TRƯỚC khi gọi build_itinerary."
        )
    if not budget_tier or budget_tier not in _VALID_BUDGET:
        return (
            "❌ TOOL_ERROR: `budget_tier` chưa được user xác nhận. "
            "Hãy dùng tool `clarify` để hỏi: "
            "'Ngân sách mỗi đêm?' với options [Thấp <3tr, Trung bình 3-6tr, Cao >6tr] TRƯỚC khi gọi build_itinerary."
        )
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
