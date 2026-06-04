"""
Vinpearl travel chatbot logic (hybrid grounding).

- Lịch trình  -> LLM sinh, NEO vào dữ liệu thật (attractions). Fallback template khi không có LLM.
- Phòng/giá   -> LẤY TỪ data cứng (vinpearl.json). Không để LLM bịa.
- Ưu đãi      -> LẤY TỪ data cứng + kiểm tra hạn theo ngày. Không bịa.
- Ngoài Vinpearl / ngoài chủ đề -> xin lỗi + điều hướng theo cấu hình trong JSON.

Toàn bộ "luật" và nội dung trả lời nằm trong backend/data/vinpearl.json để dễ sửa.
"""
import os
import json
import unicodedata
from functools import lru_cache
from typing import List, Dict, Optional

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "vinpearl.json"
)


@lru_cache(maxsize=1)
def load_data() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    return unicodedata.normalize("NFC", (text or "").lower().strip())


def _today() -> str:
    """Dùng ngày giả định trong data để demo ổn định (không phụ thuộc đồng hồ máy)."""
    return load_data().get("_meta", {}).get("today_assumed", "2026-06-04")


def _price(vnd: int) -> str:
    return f"{vnd:,}đ".replace(",", ".")


def _last_user_msg(history: List[Dict[str, str]]) -> str:
    return next((m["content"] for m in reversed(history) if m["role"] == "user"), "")


def render_links(keys: List[str]) -> str:
    """Biến danh sách tên link -> chuỗi markdown các nút bấm."""
    links = load_data().get("links", {})
    parts = [f"[{links[k]['label']}]({links[k]['url']})" for k in keys if k in links]
    return " · ".join(parts)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def detect_destination(norm: str) -> Optional[str]:
    """Trả về key địa điểm Vinpearl nếu khớp alias, ngược lại None."""
    for key, dest in load_data()["destinations"].items():
        for alias in dest.get("aliases", []):
            if _normalize(alias) in norm:
                return key
    return None


def detect_destination_from_history(history: List[Dict[str, str]]) -> Optional[str]:
    for m in reversed(history):
        key = detect_destination(_normalize(m["content"]))
        if key:
            return key
    return None


def detect_non_vinpearl(norm: str) -> Optional[str]:
    """Nếu user nhắc một địa điểm KHÔNG có Vinpearl (trong known_places) -> trả tên."""
    known = load_data()["non_vinpearl_redirect"]["known_places"]
    for place in known:
        if _normalize(place) in norm:
            return place
    return None


STYLE_KWS = {
    "nghỉ dưỡng": ["nghỉ dưỡng", "nghi duong", "thư giãn", "relax", "resort"],
    "vui chơi": ["vui chơi", "vui choi", "giải trí", "vinwonders", "safari", "chơi"],
    "văn hoá": ["văn hoá", "văn hóa", "van hoa", "di tích", "truyền thống"],
}

DEAL_KWS = ["ưu đãi", "uu dai", "khuyến mãi", "khuyen mai", "giảm giá", "giam gia",
            "combo", "voucher", "khuyến mại", "deal", "promotion"]
ROOM_KWS = ["phòng", "phong", "khách sạn", "khach san", "resort", "lưu trú", "luu tru",
            "giá phòng", "gia phong", "ở đâu", "nghỉ ở"]
BOOKING_KWS = ["đặt phòng", "dat phong", "book phòng", "đặt khách sạn", "muốn đặt", "đặt room"]
ITIN_KWS = ["lịch trình", "lich trinh", "đi chơi", "tham quan", "kế hoạch", "ke hoach",
            "itinerary", "đi đâu", "chơi gì", "ngày", "đêm", "tour"]


def detect_style(norm: str) -> Optional[str]:
    for style, kws in STYLE_KWS.items():
        if any(k in norm for k in kws):
            return style
    return None


def detect_style_from_history(history: List[Dict[str, str]]) -> Optional[str]:
    for m in reversed(history):
        if m["role"] == "user":
            s = detect_style(_normalize(m["content"]))
            if s:
                return s
    return None


def has_inscope_keyword(norm: str) -> bool:
    kws = load_data()["scope"]["in_scope_keywords"]
    return any(_normalize(k) in norm for k in kws)


def is_greeting(norm: str) -> bool:
    kws = load_data()["scope"]["greeting_keywords"]
    return any(norm == _normalize(k) or norm.startswith(_normalize(k) + " ") for k in kws) or norm in (
        "chào", "chào bạn",
    )


def classify_intent(norm: str) -> Optional[str]:
    if any(k in norm for k in DEAL_KWS):
        return "deal"
    if any(k in norm for k in BOOKING_KWS):
        return "booking"
    if any(k in norm for k in ROOM_KWS):
        return "room"
    if any(k in norm for k in ITIN_KWS) or detect_style(norm):
        return "itinerary"
    return None


# ---------------------------------------------------------------------------
# Deterministic replies (room / deal / redirect) — KHÔNG dùng LLM
# ---------------------------------------------------------------------------

def _hotels(loc: str) -> List[dict]:
    return load_data()["hotels"].get(loc, [])


def _hotel_by_id(loc: str, hid: str) -> Optional[dict]:
    return next((h for h in _hotels(loc) if h["id"] == hid), None)


def rooms_reply(loc: str) -> str:
    data = load_data()
    dest = data["destinations"][loc]
    hotels = _hotels(loc)

    # Có còn phòng available ở địa điểm này không?
    any_available = any(r["status"] == "available" for h in hotels for r in h["rooms"])
    if not any_available:
        r = data["redirects"]["no_room"]
        msg = r["message"].format(hotel=hotels[0]["name"] if hotels else dest["name"])
        return f"{msg}\n\n{render_links(r['show_links'])}"

    lines = [f"🛏️ **Phòng Vinpearl tại {dest['name']}:**\n"]
    for h in hotels:
        lines.append(f"**🏨 {h['name']}** ({h['area']} · {'⭐' * h['star']})")
        for room in h["rooms"]:
            if room["status"] == "available":
                lines.append(f"   - {room['type']} — **{_price(room['price_vnd'])}**/đêm (còn phòng)")
            else:
                lines.append(f"   - ~~{room['type']} — {_price(room['price_vnd'])}/đêm~~ (❌ hết phòng)")
        book = h.get("booking_url")
        if book:
            lines.append(f"   👉 [Đặt phòng tại đây]({book})")
        lines.append("")
    lines.append(f"---\n*📚 [Xem nguồn]({hotels[0].get('source', '')})*")
    return "\n".join(lines)


def deals_reply(loc: str) -> str:
    data = load_data()
    dest = data["destinations"][loc]
    today = _today()
    all_deals = data["deals"].get(loc, [])
    valid = [d for d in all_deals if d["valid_from"] <= today <= d["valid_to"]]

    if not valid:
        r = data["redirects"]["no_deal"]
        msg = r["message"].format(place=dest["name"])
        return f"{msg}\n\n{render_links(r['show_links'])}"

    lines = [f"🎁 **Ưu đãi đang áp dụng tại {dest['name']}** (hôm nay {today}):\n"]
    for d in valid:
        hotel = _hotel_by_id(loc, d.get("applies_to", ""))
        hotel_name = hotel["name"] if hotel else "Vinpearl"
        lines.append(
            f"**{d['title']}** — `{d['discount']}`\n"
            f"   - Áp dụng: {hotel_name}\n"
            f"   - Điều kiện: {d['conditions']}\n"
            f"   - Hiệu lực: {d['valid_from']} → {d['valid_to']}\n"
            f"   - [Xem nguồn]({d.get('source', '')})\n"
        )
    return "\n".join(lines)


def non_vinpearl_reply(place: str) -> str:
    data = load_data()
    cfg = data["non_vinpearl_redirect"]
    msg = cfg["default"]["message"].format(place=place.title())
    nearest_key = cfg["known_places"].get(place, {}).get("nearest")
    extra = ""
    if nearest_key and nearest_key in data["destinations"]:
        near = data["destinations"][nearest_key]["name"]
        extra = f"\n\n💡 Gần đó, Vinpearl có cơ sở tại **{near}** — bạn có muốn xem không?"
    return f"{msg}{extra}\n\n{render_links(cfg['default']['show_links'])}"


def out_of_scope_reply() -> str:
    return load_data()["scope"]["out_of_scope_message"]


def greeting_reply() -> str:
    return load_data()["scope"]["greeting_message"]


def ask_destination_reply() -> str:
    names = [d["name"] for d in load_data()["destinations"].values()]
    return (
        "Bạn muốn tìm hiểu điểm đến Vinpearl nào? 🗺️\n\n"
        + " · ".join(f"**{n}**" for n in names)
        + "\n\nVí dụ: *'lịch trình Phú Quốc 2N1Đ thích vui chơi'*"
    )


def low_confidence_reply(loc: str) -> str:
    dest = load_data()["destinations"][loc]
    return (
        f"Bạn muốn lịch trình **{dest['name']}** theo phong cách nào, và đi mấy ngày? 🤔\n\n"
        "- 🏖️ **Nghỉ dưỡng** — resort, spa, biển\n"
        "- 🎢 **Vui chơi** — VinWonders, Safari, giải trí\n"
        "- 🎭 **Văn hoá** — tham quan, trải nghiệm truyền thống\n\n"
        "*(Cho tôi biết để gợi ý đúng nhu cầu, tránh đoán bừa.)*"
    )


# ---------------------------------------------------------------------------
# Itinerary — LLM grounded, fallback template
# ---------------------------------------------------------------------------

def _build_itinerary_system_prompt(loc: str, style: str, duration: str) -> str:
    dest = load_data()["destinations"][loc]
    lines = [
        "Bạn là trợ lý lập lịch trình du lịch của Vinpearl.",
        "CHỈ được xếp lịch từ DANH SÁCH ĐIỂM THAM QUAN dưới đây. TUYỆT ĐỐI không thêm địa điểm ngoài danh sách.",
        "KHÔNG nói về giá phòng, không tự bịa ưu đãi (phần đó hệ thống sẽ tự thêm).",
        f"Trả lời bằng tiếng Việt. Xuất timeline theo từng ngày, mỗi ngày chia Sáng/Chiều/Tối,",
        "mỗi hoạt động kèm MỘT dòng LÝ DO ngắn. Tôn trọng giờ mở cửa.",
        "",
        f"ĐỊA ĐIỂM: {dest['name']} ({dest['region']})",
        f"GIỚI THIỆU: {dest['intro']}",
        f"SỐ NGÀY: {duration} · PHONG CÁCH: {style} · HÔM NAY: {_today()}",
        "",
        "ĐIỂM THAM QUAN CHO PHÉP:",
    ]
    for a in dest.get("attractions", []):
        lines.append(f"- {a['name']} (giờ mở: {a.get('open', 'N/A')}) — {a.get('note', '')}")
    return "\n".join(lines)


async def _llm_itinerary(loc: str, style: str, duration: str,
                         history: List[Dict[str, str]]) -> Optional[str]:
    """Gọi LLM với prompt đã neo dữ liệu. Trả None nếu không có provider / lỗi."""
    system_prompt = _build_itinerary_system_prompt(loc, style, duration)
    try:
        from services.chatbot import detect_provider
        provider = detect_provider()
        msgs = [{"role": m["role"], "content": m["content"]} for m in history] or [
            {"role": "user", "content": f"Lịch trình {duration} {style}"}
        ]

        if provider == "gemini":
            from services.chatbot import _call_gemini
            return await _call_gemini(msgs, os.getenv("GEMINI_API_KEY", ""),
                                      os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
                                      system_prompt=system_prompt)
        if provider == "openai":
            from services.chatbot import _call_openai_compat
            return await _call_openai_compat(msgs, os.getenv("OPENAI_API_KEY", ""),
                                             os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                                             system_prompt=system_prompt)
        if provider == "claude":
            from services.chatbot import _call_claude
            return await _call_claude(msgs, os.getenv("CLAUDE_API_KEY", ""),
                                      os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
                                      system_prompt=system_prompt)
        if provider == "openrouter":
            from services.chatbot import _call_openai_compat
            return await _call_openai_compat(msgs, os.getenv("OPENROUTER_API_KEY", ""),
                                             os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
                                             base_url="https://openrouter.ai/api/v1",
                                             system_prompt=system_prompt)
        if provider == "ollama":
            from services.chatbot import _call_openai_compat
            base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1"
            return await _call_openai_compat(msgs, "ollama",
                                             os.getenv("OLLAMA_MODEL", "llama3"),
                                             base_url=base, system_prompt=system_prompt)
    except Exception as e:
        print(f"[vinpearl][llm_itinerary] {e}")
    return None


def _fallback_itinerary(loc: str, style: str, duration: str) -> str:
    """Lịch trình template cứng khi không có LLM."""
    itins = load_data()["itineraries"].get(loc, [])
    chosen = next((i for i in itins if i["style"] == style), None) or (itins[0] if itins else None)
    if not chosen:
        return f"🗓️ Lịch trình {duration} tại đây đang được cập nhật."

    lines = [f"🗓️ **Lịch trình {chosen['duration']} {load_data()['destinations'][loc]['name']} — {chosen['style']}**\n"]
    for day in chosen["days"]:
        lines.append(f"**Ngày {day['day']}:**")
        for slot, label in (("morning", "🌅 Sáng"), ("afternoon", "☀️ Chiều"), ("evening", "🌙 Tối")):
            if slot in day:
                s = day[slot]
                lines.append(f"- {label}: **{s['activity']}** — _{s['reason']}_")
        lines.append("")
    lines.append(f"---\n*📚 [Xem nguồn]({chosen.get('source', '')})*")
    return "\n".join(lines)


def _suggest_hotel_block(loc: str) -> str:
    """Gợi ý 1 khu phòng (DATA CỨNG) kèm giá + link đặt."""
    itins = load_data()["itineraries"].get(loc, [])
    hid = itins[0].get("suggest_hotel") if itins else None
    hotel = _hotel_by_id(loc, hid) if hid else (_hotels(loc)[0] if _hotels(loc) else None)
    if not hotel:
        return ""
    avail = next((r for r in hotel["rooms"] if r["status"] == "available"), None)
    price_line = f" — từ **{_price(avail['price_vnd'])}**/đêm" if avail else " — (đang cập nhật phòng)"
    book = hotel.get("booking_url", "")
    book_line = f" · [Đặt phòng]({book})" if book else ""
    return (
        f"\n\n🏨 **Gợi ý lưu trú:** {hotel['name']}{price_line}{book_line}"
    )


def _deal_inline_block(loc: str) -> str:
    """Thêm 1 ưu đãi CÒN HẠN (data cứng); nếu không có thì nói rõ, không bịa."""
    data = load_data()
    today = _today()
    valid = [d for d in data["deals"].get(loc, []) if d["valid_from"] <= today <= d["valid_to"]]
    if valid:
        d = valid[0]
        return f"\n🎁 **Ưu đãi áp dụng:** {d['title']} (`{d['discount']}`) · [Xem nguồn]({d.get('source', '')})"
    return f"\n🎁 *Hiện chưa có ưu đãi phù hợp cho thời điểm này.* {render_links(['promotions'])}"


async def itinerary_reply(loc: str, norm: str, history: List[Dict[str, str]]) -> str:
    style = detect_style(norm) or detect_style_from_history(history)
    duration = "2N1Đ"  # build slice cố định 2N1Đ; có thể mở rộng sau

    # Low-confidence: chưa rõ phong cách -> hỏi lại thay vì đoán bừa
    if not style:
        return low_confidence_reply(loc)

    timeline = await _llm_itinerary(loc, style, duration, history)
    if not timeline:
        timeline = _fallback_itinerary(loc, style, duration)

    return timeline + _suggest_hotel_block(loc) + _deal_inline_block(loc)


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------

async def respond(history: List[Dict[str, str]]) -> str:
    last = _last_user_msg(history)
    norm = _normalize(last)

    intent = classify_intent(norm)
    cur_dest = detect_destination(norm)
    non_vp = detect_non_vinpearl(norm)

    # 1. Chào hỏi (không kèm địa điểm/intent)
    if is_greeting(norm) and not cur_dest and not intent:
        return greeting_reply()

    # 2. Nhắc địa điểm KHÔNG có Vinpearl (và không nhắc địa điểm Vinpearl nào) -> điều hướng
    if non_vp and not cur_dest:
        return non_vinpearl_reply(non_vp)

    # 3. Ngoài chủ đề: không intent, không địa điểm, không từ khoá du lịch
    loc = cur_dest or detect_destination_from_history(history)
    if not intent and not loc and not has_inscope_keyword(norm):
        return out_of_scope_reply()

    # 4. Trong phạm vi nhưng chưa rõ địa điểm -> hỏi địa điểm
    if not loc:
        return ask_destination_reply()

    # 5. Có địa điểm Vinpearl hợp lệ -> route theo 3 chức năng
    if intent == "deal":
        return deals_reply(loc)
    if intent in ("room", "booking"):
        return rooms_reply(loc)
    # mặc định: lịch trình (LLM grounded)
    return await itinerary_reply(loc, norm, history)
