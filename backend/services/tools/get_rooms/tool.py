from __future__ import annotations


_DEST_NAME = {1: "Phú Quốc", 2: "Nha Trang", 3: "Nam Hội An", 4: "Cửa Hội", 5: "Hải Phòng"}


def get_rooms(
    destination_id: int = 1,
    who: str = "couple",
    budget_tier: str = "trung",
    style: str = "cả hai",
) -> str:
    """Return a room comparison table for a Vinpearl destination."""
    try:
        # Lazy import to avoid circular deps — heavy logic lives in chatbot.py helpers
        from services.chatbot import _get_all_dest_rooms, _build_rooms_comparison  # noqa: PLC0415
        dest_name = _DEST_NAME.get(int(destination_id), "Phú Quốc")
        all_rooms = _get_all_dest_rooms(int(destination_id))
        return _build_rooms_comparison(all_rooms, who, budget_tier, style, dest_name, nights=1)
    except Exception as exc:
        return f"Lỗi lấy danh sách phòng: {exc}"
