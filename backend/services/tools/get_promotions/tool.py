from __future__ import annotations


_DEST_NAME = {1: "Phú Quốc", 2: "Nha Trang", 3: "Nam Hội An", 4: "Cửa Hội", 5: "Hải Phòng"}


def get_promotions(destination_id: int = 0) -> str:
    """Return current Vinpearl promotions. destination_id=0 means all destinations."""
    try:
        from services.chatbot import VINPEARL_DEALS  # noqa: PLC0415
        dest_id = int(destination_id)

        # If no specific destination, show promotions for ALL 5 destinations
        if dest_id == 0:
            sections = []
            for did, dname in _DEST_NAME.items():
                section = _get_dest_promotions(did, dname)
                if section:
                    sections.append(section)
            return "\n\n".join(sections) if sections else "Hiện chưa có ưu đãi mới."

        dest_name = _DEST_NAME.get(dest_id, "Phú Quốc")
        return _get_dest_promotions(dest_id, dest_name) or f"Hiện chưa có ưu đãi tại {dest_name}."
    except Exception as exc:
        return f"Lỗi lấy ưu đãi: {exc}"


def _get_dest_promotions(dest_id: int, dest_name: str) -> str:
    from services.chatbot import VINPEARL_DEALS  # noqa: PLC0415
    try:
        from database import get_vp_promotions
        db_deals = get_vp_promotions(dest_id, 0)
    except Exception:
        db_deals = []
    deals = db_deals or VINPEARL_DEALS
    rows = []
    for d in deals:
        disc = d.get("discount_value") or d.get("discount", "")
        disc_str = f"{int(disc)}%" if isinstance(disc, (int, float)) and disc else str(disc)
        cond = d.get("condition_text") or d.get("condition", "")
        url  = d.get("source_url", "https://vinpearl.com/vi/khuyen-mai")
        title = d.get("name") or d.get("title", "")
        rows.append(f"| **{title}** | {disc_str} | {cond} | [Xem]({url}) |")
    if not rows:
        return ""
    return (
        f"### 🎁 Ưu đãi Vinpearl {dest_name}\n\n"
        "| Ưu đãi | Giảm | Điều kiện | Chi tiết |\n"
        "|---|:---:|---|:---:|\n"
        + "\n".join(rows)
    )
