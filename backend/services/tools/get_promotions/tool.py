from __future__ import annotations


_DEST_NAME = {1: "Phú Quốc", 2: "Nha Trang", 3: "Nam Hội An", 4: "Cửa Hội", 5: "Hải Phòng"}


def get_promotions(destination_id: int = 1) -> str:
    """Return current Vinpearl promotions for a destination."""
    try:
        from services.chatbot import VINPEARL_DEALS  # noqa: PLC0415
        dest_id  = int(destination_id)
        dest_name = _DEST_NAME.get(dest_id, "Phú Quốc")
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
        return (
            f"### 🎁 Ưu đãi Vinpearl {dest_name}\n\n"
            "| Ưu đãi | Giảm | Điều kiện | Chi tiết |\n"
            "|---|:---:|---|:---:|\n"
            + "\n".join(rows)
        )
    except Exception as exc:
        return f"Lỗi lấy ưu đãi: {exc}"
