import os
import re
import sys
# Allow importing database.py from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import List, Dict, Optional

# ---------------------------------------------------------------------------
# Multi-provider AI backend
# Supported: openai | gemini | claude | openrouter | ollama
#
# Auto-detection order (if AI_PROVIDER not set):
#   OPENAI_API_KEY → GEMINI_API_KEY → CLAUDE_API_KEY → OPENROUTER_API_KEY → ollama
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """Bạn là VinBot — trợ lý AI chuyên lên lịch trình du lịch Vinpearl Phú Quốc.
Hỗ trợ mọi độ dài chuyến đi (2 ngày, 3 ngày, 5 ngày... đều được).
Quy trình: hỏi 3 câu (đi với ai / ngân sách / thích biển hay vui chơi),
rồi đề xuất lịch trình chi tiết theo từng ngày (sáng/chiều/tối),
gắn 1 khu phòng Vinpearl phù hợp và tối đa 1 ưu đãi đang áp dụng.
Quy tắc cứng:
- CHỈ đề xuất phòng/ưu đãi có trong dữ liệu thật — không bịa.
- Nếu không có ưu đãi phù hợp → nói thẳng "chưa có ưu đãi phù hợp".
- VinWonders + Safari KHÔNG đi cùng 1 ngày (Safari đóng 16:30, không kịp sau VinWonders).
- Luôn trả lời tiếng Việt. Thân thiện, có lý do cho từng lựa chọn."""

FALLBACK_RESPONSES = {
    "xin chào": "Xin chào! Tôi là TravelBot 🌍 Tôi có thể giúp bạn lên kế hoạch du lịch, gợi ý điểm đến, khách sạn và nhiều hơn nữa. Bạn muốn đi đâu?",
    "hello": "Hello! I'm TravelBot 🌍 I can help you plan trips, find destinations, hotels and activities. Where would you like to go?",
    "hi": "Hi there! I'm TravelBot 🌍 Ready to help you plan your next adventure. Where are you thinking of traveling?",
    "hà nội": (
        "Hà Nội là thủ đô ngàn năm văn hiến của Việt Nam! 🏛️\n\n"
        "**Điểm tham quan nổi bật:**\n"
        "- Hồ Hoàn Kiếm & Tháp Rùa\n"
        "- Văn Miếu Quốc Tử Giám\n"
        "- Phố cổ 36 phố phường\n"
        "- Lăng Bác Hồ\n\n"
        "**Ẩm thực phải thử:**\n"
        "- Phở Bát Đàn\n"
        "- Bún chả Hương Liên\n"
        "- Chả cá Lã Vọng\n\n"
        "Bạn dự định đi mấy ngày?\n\n"
        "---\n"
        "*📚 Nguồn: [Vietnam Tourism](https://vietnam.travel/places-to-go/northern-vietnam/hanoi) · "
        "[Lonely Planet Hanoi](https://www.lonelyplanet.com/vietnam/hanoi) · "
        "[TripAdvisor Hanoi](https://www.tripadvisor.com/Tourism-g293924-Hanoi-Vacations.html)*"
    ),
    "đà nẵng": (
        "Đà Nẵng – thành phố đáng sống! 🌊\n\n"
        "**Điểm nổi bật:**\n"
        "- Bãi biển Mỹ Khê *(CNN Travel bình chọn top 6 bãi biển đẹp nhất hành tinh)*\n"
        "- Cầu Rồng phun lửa (thứ 7 & CN)\n"
        "- Bà Nà Hills & Cầu Vàng\n"
        "- Phố cổ Hội An (cách 30 phút)\n\n"
        "**Thời điểm tốt nhất:** Tháng 1–8 *(ít mưa, nắng đẹp)*\n\n"
        "Bạn muốn biết thêm về khách sạn hay hoạt động?\n\n"
        "---\n"
        "*📚 Nguồn: [Vietnam Tourism – Đà Nẵng](https://vietnam.travel/places-to-go/central-vietnam/da-nang) · "
        "[CNN Travel](https://edition.cnn.com/travel) · "
        "[Lonely Planet Da Nang](https://www.lonelyplanet.com/vietnam/da-nang)*"
    ),
    "hội an": (
        "Hội An – Phố cổ huyền diệu! 🏮\n\n"
        "**Không thể bỏ qua:**\n"
        "- Phố đèn lồng Hội An *(Di sản Văn hoá Thế giới UNESCO 1999)*\n"
        "- Chùa Cầu Nhật Bản\n"
        "- Làng rau Trà Quế\n"
        "- Nhà cổ Tấn Ký, Phùng Hưng\n\n"
        "**Ẩm thực đặc sắc:**\n"
        "- Cao lầu · Mì Quảng · Bánh mì Phượng\n\n"
        "Thích chụp ảnh? Đến lễ hội đèn lồng vào 14 âm lịch hàng tháng nhé!\n\n"
        "---\n"
        "*📚 Nguồn: [UNESCO – Hội An](https://whc.unesco.org/en/list/948) · "
        "[Lonely Planet Hoi An](https://www.lonelyplanet.com/vietnam/hoi-an) · "
        "[Vietnam Tourism](https://vietnam.travel/places-to-go/central-vietnam/hoi-an)*"
    ),
    "sapa": (
        "Sa Pa – Vùng cao mây phủ! 🏔️\n\n"
        "**Trải nghiệm:**\n"
        "- Trekking Fansipan *(3,143m – Nóc nhà Đông Dương)*\n"
        "- Ruộng bậc thang Mù Cang Chải *(tháng 9–10 lúa vàng đẹp nhất)*\n"
        "- Bản làng người H'Mông, Dao Đỏ\n"
        "- Chợ phiên Bắc Hà *(Chủ nhật hàng tuần)*\n\n"
        "**Lưu ý:** Mang áo ấm, nhiệt độ có thể xuống 5°C vào mùa đông.\n\n"
        "Bạn muốn đặt tour trekking không?\n\n"
        "---\n"
        "*📚 Nguồn: [Vietnam Tourism – Sapa](https://vietnam.travel/places-to-go/northern-vietnam/sapa) · "
        "[Lonely Planet Sapa](https://www.lonelyplanet.com/vietnam/the-far-north/sapa) · "
        "[Sun World Fansipan](https://fansipanlegend.sunworld.vn)*"
    ),
    "phú quốc": (
        "Phú Quốc – Đảo Ngọc Việt Nam! 🌴\n\n"
        "**Điểm đến:**\n"
        "- Bãi Sao, Bãi Dài, Bãi Trường\n"
        "- VinWonders Phú Quốc & Vinpearl Safari\n"
        "- Chợ đêm Dinh Cậu\n"
        "- Làng chài Hàm Ninh\n\n"
        "**Đặc sản:** Nước mắm Phú Quốc *(chỉ dẫn địa lý EU)*, nhum biển, ghẹ hấp\n\n"
        "**Bay từ HCM:** ~1 giờ | Từ HN: ~2 giờ\n"
        "**Mùa đẹp nhất:** Tháng 11 – tháng 4\n\n"
        "---\n"
        "*📚 Nguồn: [Vietnam Tourism – Phú Quốc](https://vietnam.travel/places-to-go/southern-vietnam/phu-quoc) · "
        "[Lonely Planet Phu Quoc](https://www.lonelyplanet.com/vietnam/phu-quoc-island) · "
        "[TripAdvisor Phú Quốc](https://www.tripadvisor.com/Tourism-g298082-Phu_Quoc-Vacations.html)*"
    ),
    "bangkok": (
        "Bangkok – City of Angels! 🛕\n\n"
        "**Must-see:**\n"
        "- Grand Palace & Wat Phra Kaew *(Thailand's most sacred temple)*\n"
        "- Wat Arun (Temple of Dawn)\n"
        "- Chatuchak Weekend Market *(15,000+ stalls)*\n"
        "- Khao San Road · Floating Markets\n\n"
        "**Food:** Pad Thai · Tom Yum · Mango Sticky Rice\n\n"
        "**Getting around:** BTS Skytrain, MRT, Grab\n\n"
        "How many days are you planning?\n\n"
        "---\n"
        "*📚 Sources: [TAT – Tourism Authority of Thailand](https://www.tourismthailand.org/Destinations/Provinces/Bangkok/479) · "
        "[Lonely Planet Bangkok](https://www.lonelyplanet.com/thailand/bangkok) · "
        "[CNN Travel Bangkok](https://edition.cnn.com/travel/destinations/bangkok)*"
    ),
    "paris": (
        "Paris – The City of Light! 🗼\n\n"
        "**Must-see:**\n"
        "- Eiffel Tower *(324m, built 1889)*\n"
        "- Louvre Museum *(world's largest art museum)*\n"
        "- Notre-Dame Cathedral\n"
        "- Montmartre & Sacré-Cœur\n"
        "- Seine River Cruise\n\n"
        "**Food:** Croissants · Crêpes · French onion soup\n\n"
        "**Best time:** April–June, Sept–Oct\n\n"
        "Would you like hotel or restaurant recommendations?\n\n"
        "---\n"
        "*📚 Sources: [Paris Tourist Office](https://www.parisinfo.com) · "
        "[Lonely Planet Paris](https://www.lonelyplanet.com/france/paris) · "
        "[TripAdvisor Paris](https://www.tripadvisor.com/Tourism-g187147-Paris_Ile_de_France-Vacations.html)*"
    ),
    "tokyo": (
        "Tokyo – Where tradition meets future! 🗾\n\n"
        "**Top spots:**\n"
        "- Shibuya Crossing *(world's busiest pedestrian crossing)*\n"
        "- Senso-ji Temple (Asakusa) *(Tokyo's oldest temple, 645 AD)*\n"
        "- Shinjuku & Harajuku\n"
        "- teamLab Borderless\n"
        "- Mount Fuji day trip\n\n"
        "**Food:** Ramen · Sushi · Yakitori · Wagyu\n\n"
        "**Best time:** March–April (Cherry blossom) or November\n\n"
        "Need a Tokyo itinerary?\n\n"
        "---\n"
        "*📚 Sources: [Japan Tourism Agency](https://www.mlit.go.jp/kankocho/en) · "
        "[Lonely Planet Tokyo](https://www.lonelyplanet.com/japan/tokyo) · "
        "[Tokyo Tourism](https://www.gotokyo.org/en)*"
    ),
}


# ---------------------------------------------------------------------------
# Provider detection
# ---------------------------------------------------------------------------

def detect_provider() -> str:
    """Return the active provider name."""
    explicit = os.getenv("AI_PROVIDER", "").lower().strip()
    if explicit in ("openai", "gemini", "claude", "openrouter", "ollama"):
        return explicit
    # Auto-detect by available keys
    if os.getenv("OPENAI_API_KEY", "").strip():
        return "openai"
    if os.getenv("GEMINI_API_KEY", "").strip():
        return "gemini"
    if os.getenv("CLAUDE_API_KEY", "").strip():
        return "claude"
    if os.getenv("OPENROUTER_API_KEY", "").strip():
        return "openrouter"
    return "ollama"  # default: local Ollama


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Token / cost helpers
# ---------------------------------------------------------------------------

# Price per 1 000 tokens in USD {model_prefix: (input, output)}
_MODEL_PRICE_PER_1K: Dict[str, tuple] = {
    # OpenAI
    "gpt-4o":              (0.005,   0.015),
    "gpt-4-turbo":         (0.01,    0.03),
    "gpt-4":               (0.03,    0.06),
    "gpt-3.5-turbo":       (0.0005,  0.0015),
    # Gemini
    "gemini-1.5-flash":    (0.000075, 0.0003),
    "gemini-1.5-pro":      (0.00125,  0.005),
    "gemini-2.0-flash":    (0.0001,   0.0004),
    # Claude
    "claude-3-haiku":      (0.00025,  0.00125),
    "claude-3-sonnet":     (0.003,    0.015),
    "claude-3-opus":       (0.015,    0.075),
    "claude-3-5-sonnet":   (0.003,    0.015),
}


def _calc_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return estimated USD cost. Falls back to gpt-3.5-turbo rates if model unknown."""
    for prefix, (in_price, out_price) in _MODEL_PRICE_PER_1K.items():
        if model.startswith(prefix):
            return (input_tokens * in_price + output_tokens * out_price) / 1_000
    # Generic fallback: $0.001 / 1K tokens
    return (input_tokens + output_tokens) * 0.001 / 1_000


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token (works for Vietnamese too)."""
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Provider implementations — each returns (reply: str, usage: dict)
# ---------------------------------------------------------------------------

async def _call_openai_compat(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    base_url: str | None = None,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple:
    """OpenAI / OpenRouter / Ollama — returns (reply, usage_dict)."""
    from openai import AsyncOpenAI

    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    client = AsyncOpenAI(**kwargs)
    messages = [{"role": "system", "content": system_prompt}] + history
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    reply = response.choices[0].message.content.strip()
    usage = getattr(response, "usage", None)
    input_t  = usage.prompt_tokens     if usage else _estimate_tokens(" ".join(m["content"] for m in messages))
    output_t = usage.completion_tokens if usage else _estimate_tokens(reply)
    return reply, {
        "input_tokens":  input_t,
        "output_tokens": output_t,
        "total_tokens":  input_t + output_t,
        "cost_usd":      _calc_cost(model, input_t, output_t),
    }


async def _call_gemini(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple:
    """Google Gemini — returns (reply, usage_dict)."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    gemini_history = []
    for msg in history[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    last_message = history[-1]["content"] if history else ""

    gemini_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt,
    )
    chat = gemini_model.start_chat(history=gemini_history)
    response = await chat.send_message_async(last_message)
    reply = response.text.strip()
    meta = getattr(response, "usage_metadata", None)
    input_t  = getattr(meta, "prompt_token_count",     None) or _estimate_tokens(last_message)
    output_t = getattr(meta, "candidates_token_count", None) or _estimate_tokens(reply)
    return reply, {
        "input_tokens":  input_t,
        "output_tokens": output_t,
        "total_tokens":  input_t + output_t,
        "cost_usd":      _calc_cost(model, input_t, output_t),
    }


async def _call_claude(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> tuple:
    """Anthropic Claude — returns (reply, usage_dict)."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    response = await client.messages.create(
        model=model,
        system=system_prompt,
        messages=messages,
        max_tokens=800,
    )
    reply = response.content[0].text.strip()
    usage = getattr(response, "usage", None)
    input_t  = getattr(usage, "input_tokens",  None) or _estimate_tokens(" ".join(m["content"] for m in messages))
    output_t = getattr(usage, "output_tokens", None) or _estimate_tokens(reply)
    return reply, {
        "input_tokens":  input_t,
        "output_tokens": output_t,
        "total_tokens":  input_t + output_t,
        "cost_usd":      _calc_cost(model, input_t, output_t),
    }


# ---------------------------------------------------------------------------
# Fallback (rule-based)
# ---------------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase, strip diacritics cơ bản để fuzzy match typo."""
    import unicodedata
    text = text.lower().strip()
    # Chuẩn hoá unicode NFC trước
    text = unicodedata.normalize("NFC", text)
    return text


# Map keyword → city/topic, hỗ trợ cả typo phổ biến
KEYWORD_MAP: Dict[str, str] = {
    # Hà Nội
    "hà nội": "hà nội", "ha noi": "hà nội", "hanoi": "hà nội",
    # Đà Nẵng
    "đà nẵng": "đà nẵng", "da nang": "đà nẵng", "danang": "đà nẵng",
    # Hội An
    "hội an": "hội an", "hoi an": "hội an", "hoian": "hội an",
    # Sapa
    "sapa": "sapa", "sa pa": "sapa",
    # Phú Quốc
    "phú quốc": "phú quốc", "phu quoc": "phú quốc", "phuquoc": "phú quốc",
    # Bangkok
    "bangkok": "bangkok", "bkk": "bangkok",
    # Paris
    "paris": "paris",
    # Tokyo
    "tokyo": "tokyo",
}

# Map topic keyword → response key
TOPIC_MAP: Dict[str, str] = {
    "khách sạn": "hotel", "khach san": "hotel", "khạchs sạn": "hotel",
    "hotel": "hotel", "hotl": "hotel", "htoel": "hotel",
    "nhà nghỉ": "hotel", "resort": "hotel",
    "ăn": "food", "đặc sản": "food", "nhà hàng": "food", "quán": "food", "food": "food", "ẩm thực": "food",
    "đặt xe": "transport", "xe": "transport", "taxi": "transport", "phương tiện": "transport",
    "thời tiết": "weather", "mưa": "weather", "nắng": "weather", "mùa": "weather",
    "vé": "ticket", "bay": "ticket", "máy bay": "ticket", "flight": "ticket",
    "lịch trình": "itinerary", "itinerary": "itinerary", "kế hoạch": "itinerary", "tour": "itinerary",
}

CITY_HOTEL_INFO: Dict[str, str] = {
    "đà nẵng": (
        "Khách sạn tại **Đà Nẵng** theo ngân sách:\n\n"
        "💎 **Cao cấp (>3 triệu/đêm):**\n"
        "- InterContinental Danang Sun Peninsula\n"
        "- Hyatt Regency Da Nang\n"
        "- Furama Resort Danang\n\n"
        "🏨 **Tầm trung (800k–2 triệu/đêm):**\n"
        "- Novotel Danang Premier Han River\n"
        "- Vinpearl Condotel Riverfront\n"
        "- Risemount Premier Resort\n\n"
        "🏠 **Bình dân (<800k/đêm):**\n"
        "- Nalod Hotel, Bamboo Green Hotel\n"
        "- Nhiều homestay khu Mỹ An, Phạm Văn Đồng\n\n"
        "📍 **Gợi ý khu vực:** Ở gần biển Mỹ Khê hoặc ven sông Hàn để tiện di chuyển.\n\n"
        "---\n"
        "*📚 Nguồn: [Booking.com – Đà Nẵng](https://www.booking.com/city/vn/da-nang.html) · "
        "[Agoda Da Nang](https://www.agoda.com/city/da-nang-vn.html) · "
        "[TripAdvisor Đà Nẵng Hotels](https://www.tripadvisor.com/Hotels-g298085-Da_Nang-Hotels.html)*"
    ),
    "hà nội": (
        "Khách sạn tại **Hà Nội** theo ngân sách:\n\n"
        "💎 **Cao cấp:**\n"
        "- Sofitel Legend Metropole *(biểu tượng Hà Nội từ 1901)*\n"
        "- JW Marriott Hanoi\n"
        "- Lotte Hotel Hanoi\n\n"
        "🏨 **Tầm trung:**\n"
        "- Mövenpick Hanoi, Pan Pacific Hanoi\n"
        "- Silk Path Grand Hotel\n\n"
        "🏠 **Bình dân:**\n"
        "- Nhiều hostel, guesthouse khu phố cổ Hoàn Kiếm từ 200k/đêm\n\n"
        "📍 **Gợi ý:** Ở khu phố cổ để đi bộ khám phá, hoặc Tây Hồ cho không gian yên tĩnh hơn.\n\n"
        "---\n"
        "*📚 Nguồn: [Booking.com – Hà Nội](https://www.booking.com/city/vn/hanoi.html) · "
        "[Agoda Hanoi](https://www.agoda.com/city/hanoi-vn.html) · "
        "[TripAdvisor Hanoi Hotels](https://www.tripadvisor.com/Hotels-g293924-Hanoi-Hotels.html)*"
    ),
    "hội an": (
        "Khách sạn tại **Hội An**:\n\n"
        "💎 **Cao cấp:**\n"
        "- Four Seasons The Nam Hai\n"
        "- Anantara Hội An Resort\n"
        "- Victoria Hội An Beach Resort\n\n"
        "🏨 **Tầm trung:**\n"
        "- Almanity Hội An Wellness Resort\n"
        "- Hội An Historic Hotel\n\n"
        "🏠 **Bình dân:**\n"
        "- Homestay trong phố cổ, giá từ 300k–600k/đêm\n\n"
        "📍 **Gợi ý:** Ở gần phố cổ để đi bộ, hoặc gần biển An Bàng/Cửa Đại.\n\n"
        "---\n"
        "*📚 Nguồn: [Booking.com – Hội An](https://www.booking.com/city/vn/hoi-an.html) · "
        "[Agoda Hoi An](https://www.agoda.com/city/hoi-an-vn.html) · "
        "[TripAdvisor Hội An Hotels](https://www.tripadvisor.com/Hotels-g298082-Hoi_An-Hotels.html)*"
    ),
    "sapa": (
        "Khách sạn tại **Sa Pa**:\n\n"
        "💎 **Cao cấp:**\n"
        "- Hotel de la Coupole MGallery\n"
        "- Topas Ecolodge *(view ruộng bậc thang, eco-certified)*\n\n"
        "🏨 **Tầm trung:**\n"
        "- Sapa Relax Hotel & Spa\n"
        "- Pao's Sapa Leisure Hotel\n\n"
        "🏠 **Bình dân:**\n"
        "- Homestay bản làng người H'Mông, trải nghiệm văn hoá thật sự từ 150k/đêm\n\n"
        "📍 **Gợi ý:** Ở homestay bản Cát Cát hoặc Tả Phìn để gần thiên nhiên.\n\n"
        "---\n"
        "*📚 Nguồn: [Booking.com – Sapa](https://www.booking.com/city/vn/sapa.html) · "
        "[Agoda Sapa](https://www.agoda.com/city/sapa-vn.html) · "
        "[TripAdvisor Sa Pa Hotels](https://www.tripadvisor.com/Hotels-g311304-Sapa_Lao_Cai_Province-Hotels.html)*"
    ),
    "phú quốc": (
        "Khách sạn tại **Phú Quốc**:\n\n"
        "💎 **Cao cấp:**\n"
        "- InterContinental Phú Quốc Long Beach\n"
        "- JW Marriott Phú Quốc Emerald Bay\n"
        "- Vinpearl Resort & Golf\n\n"
        "🏨 **Tầm trung:**\n"
        "- Premier Residences Phú Quốc Emerald Bay\n"
        "- Salinda Resort\n\n"
        "🏠 **Bình dân:**\n"
        "- Guesthouse khu Dương Đông, giá từ 400k/đêm\n\n"
        "📍 **Gợi ý:** Khu Bãi Trường dài bờ biển đẹp, gần trung tâm.\n\n"
        "---\n"
        "*📚 Nguồn: [Booking.com – Phú Quốc](https://www.booking.com/city/vn/phu-quoc.html) · "
        "[Agoda Phu Quoc](https://www.agoda.com/city/phu-quoc-vn.html) · "
        "[TripAdvisor Phú Quốc Hotels](https://www.tripadvisor.com/Hotels-g737051-Phu_Quoc-Hotels.html)*"
    ),
    "bangkok": (
        "Hotels in **Bangkok**:\n\n"
        "💎 **Luxury:**\n"
        "- Mandarin Oriental Bangkok *(ranked #1 hotel in Asia multiple years)*\n"
        "- The Peninsula Bangkok\n"
        "- Capella Bangkok\n\n"
        "🏨 **Mid-range:**\n"
        "- Chatrium Hotel Riverside, Avani Riverside\n\n"
        "🏠 **Budget:**\n"
        "- Khao San Road area hostels from $10/night\n\n"
        "📍 **Tip:** Stay near BTS Skytrain for easy access everywhere.\n\n"
        "---\n"
        "*📚 Sources: [Booking.com – Bangkok](https://www.booking.com/city/th/bangkok.html) · "
        "[Agoda Bangkok](https://www.agoda.com/city/bangkok-th.html) · "
        "[TripAdvisor Bangkok Hotels](https://www.tripadvisor.com/Hotels-g293916-Bangkok-Hotels.html)*"
    ),
    "tokyo": (
        "Hotels in **Tokyo**:\n\n"
        "💎 **Luxury:**\n"
        "- Aman Tokyo, The Peninsula Tokyo\n"
        "- Park Hyatt Tokyo *(featured in 'Lost in Translation')*\n\n"
        "🏨 **Mid-range:**\n"
        "- Keio Plaza Hotel, Shinjuku Granbell Hotel\n\n"
        "🏠 **Budget:**\n"
        "- Capsule hotels from ¥3,000/night\n"
        "- Hostels in Asakusa or Shinjuku\n\n"
        "📍 **Tip:** Stay near Shinjuku or Shibuya for best transport links.\n\n"
        "---\n"
        "*📚 Sources: [Booking.com – Tokyo](https://www.booking.com/city/jp/tokyo.html) · "
        "[Agoda Tokyo](https://www.agoda.com/city/tokyo-jp.html) · "
        "[TripAdvisor Tokyo Hotels](https://www.tripadvisor.com/Hotels-g298184-Tokyo_Tokyo_Prefecture_Kanto-Hotels.html)*"
    ),
    "paris": (
        "Hotels in **Paris**:\n\n"
        "💎 **Luxury:**\n"
        "- Hôtel Ritz Paris *(opened 1898, Place Vendôme)*\n"
        "- Le Bristol Paris, Four Seasons George V\n\n"
        "🏨 **Mid-range:**\n"
        "- Citadines Apart'hotel, Ibis Styles\n\n"
        "🏠 **Budget:**\n"
        "- Hostels near Gare du Nord from €20/night\n\n"
        "📍 **Tip:** Stay in arrondissements 1–8 to be close to main attractions.\n\n"
        "---\n"
        "*📚 Sources: [Booking.com – Paris](https://www.booking.com/city/fr/paris.html) · "
        "[Agoda Paris](https://www.agoda.com/city/paris-fr.html) · "
        "[TripAdvisor Paris Hotels](https://www.tripadvisor.com/Hotels-g187147-Paris_Ile_de_France-Hotels.html)*"
    ),
}

CITY_INSPIRE: Dict[str, str] = {
    "mặc định": (
        "Đây là vài gợi ý điểm đến tuyệt vời! ✨\n\n"
        "🇻🇳 **Trong nước:**\n"
        "- **Đà Nẵng** — biển đẹp, ẩm thực phong phú, gần Hội An\n"
        "- **Sapa** — ruộng bậc thang, trekking, văn hoá dân tộc\n"
        "- **Phú Quốc** — đảo ngọc, resort sang, lặn biển\n\n"
        "🌏 **Châu Á:**\n"
        "- **Bangkok** — ẩm thực, chùa chiền, mua sắm\n"
        "- **Tokyo** — công nghệ, anime, ẩm thực Nhật\n"
        "- **Bali** — thiên nhiên, yoga, giá hợp lý\n\n"
        "Bạn thích loại hình du lịch nào — **biển**, **núi**, **văn hoá** hay **ẩm thực**?\n\n"
        "---\n"
        "*📚 Nguồn tham khảo: "
        "[Vietnam Tourism](https://vietnam.travel) · "
        "[Lonely Planet Vietnam](https://www.lonelyplanet.com/vietnam) · "
        "[CNN Travel Best Destinations 2025](https://edition.cnn.com/travel)*"
    )
}


def _extract_days(text: str) -> int | None:
    """Tìm số ngày trong tin nhắn, chấp nhận typo của 'ngày' (nagfy, ngaf, v.v.)."""
    import re
    # Match: số + từ bắt đầu bằng "ng" (mọi typo của "ngày") hoặc day/days/đêm
    m = re.search(r"(\d+)\s*(?:ngày|ngay|ng\w*|day|days|đêm|dem)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # Fallback: nếu có số 1–60 đứng một mình trong câu có từ khoá thời gian
    if any(w in text.lower() for w in ["lịch trình", "lich trinh", "itinerary", "kế hoạch", "tour", "đi", "di "]):
        m2 = re.search(r"\b([1-9]\d?)\b", text)
        if m2:
            return int(m2.group(1))
    return None


def _extract_style(text: str) -> str:
    """Detect travel style keyword."""
    styles = {
        "nghỉ dưỡng": "nghỉ dưỡng", "nghi duong": "nghỉ dưỡng", "relaxing": "nghỉ dưỡng", "resort": "nghỉ dưỡng",
        "khám phá": "khám phá", "kham pha": "khám phá", "explore": "khám phá", "adventure": "khám phá",
        "ẩm thực": "ẩm thực", "am thuc": "ẩm thực", "food": "ẩm thực", "foodie": "ẩm thực",
        "văn hoá": "văn hoá", "van hoa": "văn hoá", "culture": "văn hoá", "cultural": "văn hoá",
        "tất cả": "tất cả", "tat ca": "tất cả", "all": "tất cả", "everything": "tất cả",
    }
    t = text.lower()
    for kw, style in styles.items():
        if kw in t:
            return style
    return "tổng hợp"


# Pre-built itineraries keyed by (city, style_group)
# style_group: "nghỉ dưỡng" | "khám phá" | "ẩm thực" | default
ITINERARY_TEMPLATES: Dict[str, Dict[str, str]] = {
    "đà nẵng": {
        "nghỉ dưỡng": (
            "🗓️ **Lịch trình {days} ngày Đà Nẵng – Nghỉ dưỡng biển**\n\n"
            "**Ngày 1–2: Đến nơi & thư giãn**\n"
            "- Check-in resort ven biển Mỹ Khê (Hyatt / Furama)\n"
            "- Tắm biển, massage spa, ngắm hoàng hôn\n\n"
            "**Ngày 3–4: Bà Nà Hills**\n"
            "- Cáp treo Bà Nà, Cầu Vàng, Làng Pháp\n"
            "- Tối: Cầu Rồng phun lửa (thứ 7 / CN)\n\n"
            "**Ngày 5–6: Hội An day trip**\n"
            "- Phố cổ Hội An, thuyền trên sông Hoài\n"
            "- Ăn tối: Cao lầu, mì Quảng, bánh mì Phượng\n\n"
            "**Ngày 7–8: Làng chài & biển đảo**\n"
            "- Thuyền thúng Mỹ Khê, đảo Sơn Trà\n"
            "- Chùa Linh Ứng, ngắm bán đảo Sơn Trà\n\n"
            "**Ngày 9–10: Spa & mua sắm**\n"
            "- Spa full-day (nhiều resort có gói trọn ngày)\n"
            "- Chợ Hàn, Vincom mua đồ lưu niệm, bay về\n\n"
            "💡 **Gợi ý khách sạn nghỉ dưỡng:** InterContinental, Hyatt Regency, Furama Resort\n\n"
            "---\n"
            "*📚 Nguồn: [Vietnam Tourism – Đà Nẵng](https://vietnam.travel/places-to-go/central-vietnam/da-nang) · "
            "[Lonely Planet Da Nang](https://www.lonelyplanet.com/vietnam/da-nang)*"
        ),
        "khám phá": (
            "🗓️ **Lịch trình {days} ngày Đà Nẵng – Khám phá**\n\n"
            "**Ngày 1: Đến & khám phá trung tâm**\n"
            "- Cầu Rồng, cầu Tình Yêu, bờ sông Hàn\n\n"
            "**Ngày 2–3: Bà Nà Hills & Non Nước**\n"
            "- Bà Nà Hills cả ngày; làng đá mỹ nghệ Non Nước\n\n"
            "**Ngày 4–5: Hội An & Mỹ Sơn**\n"
            "- Phố cổ Hội An, thánh địa Mỹ Sơn (UNESCO)\n\n"
            "**Ngày 6–7: Sơn Trà & Ngũ Hành Sơn**\n"
            "- Bán đảo Sơn Trà, chùa Linh Ứng, Ngũ Hành Sơn\n\n"
            "**Ngày 8–9: Huế day trip**\n"
            "- Kinh thành Huế, lăng Tự Đức, sông Hương\n\n"
            "**Ngày 10: Biển Mỹ Khê & về**\n"
            "- Buổi sáng tắm biển, trưa mua đồ lưu niệm, bay về\n\n"
            "---\n"
            "*📚 Nguồn: [Vietnam Tourism – Đà Nẵng](https://vietnam.travel/places-to-go/central-vietnam/da-nang) · "
            "[Lonely Planet Da Nang](https://www.lonelyplanet.com/vietnam/da-nang)*"
        ),
        "ẩm thực": (
            "🗓️ **Lịch trình {days} ngày Đà Nẵng – Foodie Tour**\n\n"
            "**Ngày 1–2: Đà Nẵng classic**\n"
            "- Mì Quảng Bà Mua, Bún mắm nêm bà Lan\n"
            "- Bánh xèo bà Dưỡng, Nem lụi Cô Ba\n\n"
            "**Ngày 3–4: Chợ & street food**\n"
            "- Chợ Cồn, chợ Hàn (buổi sáng sớm)\n"
            "- Hải sản tươi sống bến cá Mỹ Khê buổi tối\n\n"
            "**Ngày 5–6: Hội An food tour**\n"
            "- Cao lầu, bánh mì Phượng, bánh bao bánh vạc\n"
            "- Lớp học nấu ăn tại Hội An\n\n"
            "**Ngày 7–8: Huế ẩm thực hoàng gia**\n"
            "- Bún bò Huế, cơm hến, bánh bèo, bánh nậm\n\n"
            "**Ngày 9–10: Kết hợp biển & cafe**\n"
            "- Cafe view biển (My Khe Sunrise, An Bang...)\n"
            "- Ốc, lẩu hải sản tất niên\n\n"
            "---\n"
            "*📚 Nguồn: [Vietnam Tourism – Đà Nẵng](https://vietnam.travel/places-to-go/central-vietnam/da-nang) · "
            "[TripAdvisor Đà Nẵng Restaurants](https://www.tripadvisor.com/Restaurants-g298085-Da_Nang.html)*"
        ),
    },
    "hà nội": {
        "nghỉ dưỡng": (
            "🗓️ **Lịch trình {days} ngày Hà Nội – Nghỉ dưỡng & Văn hoá**\n\n"
            "**Ngày 1–2: Hồ Hoàn Kiếm & phố cổ**\n"
            "- Check-in khách sạn sang khu Hoàn Kiếm\n"
            "- Đi bộ phố cổ, cà phê trứng Giảng\n\n"
            "**Ngày 3–4: Di tích lịch sử**\n"
            "- Văn Miếu, Lăng Bác, Hoàng thành Thăng Long\n\n"
            "**Ngày 5–6: Tây Hồ – Yên lặng**\n"
            "- Chùa Trấn Quốc, bún ốc nguội bà bầu\n"
            "- Cà phê Tây Hồ, spa\n\n"
            "**Ngày 7–8: Ninh Bình day trip**\n"
            "- Tràng An, Tam Cốc, Bích Động\n\n"
            "**Ngày 9–10: Mua sắm & về**\n"
            "- Phố Hàng Gai (lụa), chợ Đồng Xuân\n\n"
            "---\n"
            "*📚 Nguồn: [Vietnam Tourism – Hà Nội](https://vietnam.travel/places-to-go/northern-vietnam/hanoi) · "
            "[Lonely Planet Hanoi](https://www.lonelyplanet.com/vietnam/hanoi)*"
        ),
    },
    "hội an": {
        "nghỉ dưỡng": (
            "🗓️ **Lịch trình {days} ngày Hội An – Nghỉ dưỡng**\n\n"
            "**Ngày 1–3: Phố cổ & sông Hoài**\n"
            "- Check-in resort ven sông / gần biển An Bàng\n"
            "- Đèn lồng Hội An, thuyền sông Hoài\n\n"
            "**Ngày 4–5: Biển An Bàng & Cửa Đại**\n"
            "- Tắm biển, ăn hải sản, nghỉ ngơi\n\n"
            "**Ngày 6–7: Làng nghề & spa**\n"
            "- Làng rau Trà Quế, làng gốm Thanh Hà\n"
            "- Spa truyền thống\n\n"
            "**Ngày 8–9: Đà Nẵng day trip**\n"
            "- Bà Nà Hills hoặc Ngũ Hành Sơn\n\n"
            "**Ngày 10: Đêm phố cổ & về**\n"
            "- Lễ hội đèn lồng nếu đúng 14 âm lịch, mua quà\n\n"
            "---\n"
            "*📚 Nguồn: [UNESCO Hội An](https://whc.unesco.org/en/list/948) · "
            "[Lonely Planet Hoi An](https://www.lonelyplanet.com/vietnam/hoi-an)*"
        ),
    },
}

# Default template for any city without specific template
_DEFAULT_ITINERARY = (
    "🗓️ **Lịch trình {days} ngày {city} – {style}**\n\n"
    "**Ngày 1–2:** Đến nơi, check-in, khám phá trung tâm\n"
    "**Ngày 3–{mid}:** Tham quan các điểm nổi bật, ẩm thực địa phương\n"
    "**Ngày {mid2}–{last2}:** Day trip các vùng lân cận\n"
    "**Ngày {days}:** Mua sắm, lưu niệm, lên đường về\n\n"
    "💬 Bạn muốn tôi lên lịch trình **chi tiết từng ngày** không? "
    "Hãy cho tôi biết thêm về ngân sách và phong cách để tôi tư vấn cụ thể hơn!"
)


def _build_itinerary(city: str, days: int, style: str) -> str:
    """Trả về lịch trình dựa trên city, số ngày và phong cách."""
    city_templates = ITINERARY_TEMPLATES.get(city, {})

    # Match style group
    style_key = "nghỉ dưỡng" if style in ("nghỉ dưỡng",) else \
                "ẩm thực" if style in ("ẩm thực",) else \
                "khám phá" if style in ("khám phá", "văn hoá") else None

    template = None
    if style_key and style_key in city_templates:
        template = city_templates[style_key]
    elif "nghỉ dưỡng" in city_templates:
        template = city_templates["nghỉ dưỡng"]

    if template:
        return template.format(days=days)

    mid = max(3, days // 2)
    return _DEFAULT_ITINERARY.format(
        days=days, city=city.title(), style=style,
        mid=mid, mid2=mid + 1, last2=days - 1,
    )


def _extract_city_from_history(history: List[Dict[str, str]]) -> str | None:
    """Tìm tên thành phố được đề cập gần nhất trong lịch sử hội thoại."""
    for msg in reversed(history):
        text = _normalize(msg["content"])
        for kw, city in KEYWORD_MAP.items():
            if kw in text:
                return city
    return None


def _extract_days_from_history(history: List[Dict[str, str]]) -> int | None:
    """Tìm số ngày trong lịch sử hội thoại."""
    for msg in reversed(history):
        if msg["role"] == "user":
            d = _extract_days(msg["content"])
            if d:
                return d
    return None


def _extract_style_from_history(history: List[Dict[str, str]]) -> str:
    """Tìm phong cách du lịch trong lịch sử hội thoại."""
    for msg in reversed(history):
        if msg["role"] == "user":
            s = _extract_style(msg["content"])
            if s != "tổng hợp":
                return s
    return "tổng hợp"



# ===========================================================================
# BOOKING FLOW
# ===========================================================================

HOTEL_ROOMS_DB: Dict[str, List[Dict]] = {
    "đà nẵng": [
        {"id": 1, "name": "InterContinental Danang Sun Peninsula ⭐⭐⭐⭐⭐",
         "rooms": ["suite", "villa", "deluxe"], "price": "8–30tr/đêm",
         "phone": "+84 236 393 8888", "email": "reservations.danang@ihg.com",
         "website": "https://danang.intercontinental.com"},
        {"id": 2, "name": "Hyatt Regency Da Nang ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "twin", "suite", "gia đình", "deluxe"], "price": "4–15tr/đêm",
         "phone": "+84 236 398 1234", "email": "danang.regency@hyatt.com",
         "website": "https://www.hyatt.com/hyatt-regency/danang"},
        {"id": 3, "name": "Furama Resort Danang ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "villa"], "price": "3–12tr/đêm",
         "phone": "+84 236 384 7333", "email": "reservations@furamavietnam.com",
         "website": "https://www.furamavietnam.com"},
        {"id": 4, "name": "Novotel Danang Premier Han River ⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe", "standard"], "price": "1.5–5tr/đêm",
         "phone": "+84 236 392 9999", "email": "H8888@accor.com",
         "website": "https://novotel.accor.com/da-nang"},
        {"id": 5, "name": "Bamboo Green Hotel ⭐⭐⭐",
         "rooms": ["đơn", "đôi", "standard"], "price": "400k–900k/đêm",
         "phone": "+84 236 382 2996", "email": "info@bamboogreenhotel.com",
         "website": "https://www.bamboogreenhotel.com"},
    ],
    "hà nội": [
        {"id": 1, "name": "Sofitel Legend Metropole ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe", "villa"], "price": "7–40tr/đêm",
         "phone": "+84 24 3826 6919", "email": "reservation@sofitelhanoi.com",
         "website": "https://www.sofitel-legend-metropole-hanoi.com"},
        {"id": 2, "name": "JW Marriott Hanoi ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "twin", "suite", "deluxe", "gia đình"], "price": "5–20tr/đêm",
         "phone": "+84 24 3833 5588", "email": "mhrs.hanbul.reservations@marriott.com",
         "website": "https://www.marriott.com/hanoi"},
        {"id": 3, "name": "Lotte Hotel Hanoi ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe"], "price": "4–18tr/đêm",
         "phone": "+84 24 3333 1000", "email": "info.hanoi@lottehotel.com",
         "website": "https://www.lottehotel.com/hanoi"},
        {"id": 4, "name": "Mövenpick Hotel Hanoi ⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "standard"], "price": "2–7tr/đêm",
         "phone": "+84 24 3822 2800", "email": "hotel.hanoi@movenpick.com",
         "website": "https://www.movenpick.com/hanoi"},
    ],
    "hội an": [
        {"id": 1, "name": "Four Seasons The Nam Hai ⭐⭐⭐⭐⭐",
         "rooms": ["villa", "suite", "deluxe", "gia đình"], "price": "15–80tr/đêm",
         "phone": "+84 235 394 0000", "email": "namhai.reservations@fourseasons.com",
         "website": "https://www.fourseasons.com/hoian"},
        {"id": 2, "name": "Anantara Hội An Resort ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "villa", "deluxe"], "price": "6–25tr/đêm",
         "phone": "+84 235 391 4555", "email": "hoian@anantara.com",
         "website": "https://www.anantara.com/hoian"},
        {"id": 3, "name": "Victoria Hội An Beach Resort ⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "gia đình"], "price": "2–8tr/đêm",
         "phone": "+84 235 392 7040", "email": "hoi-an@victoriahotels.asia",
         "website": "https://www.victoriahotels.asia/hoian"},
    ],
    "sapa": [
        {"id": 1, "name": "Hotel de la Coupole MGallery ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe"], "price": "3–15tr/đêm",
         "phone": "+84 214 3688 999", "email": "H7436@accor.com",
         "website": "https://mgallery.accor.com/sapa"},
        {"id": 2, "name": "Topas Ecolodge ⭐⭐⭐⭐",
         "rooms": ["đôi", "deluxe", "bungalow", "villa"], "price": "2–6tr/đêm",
         "phone": "+84 214 3872 404", "email": "sapa@topas-ecolodge.com",
         "website": "https://www.topas-ecolodge.com"},
        {"id": 3, "name": "Sapa Relax Hotel & Spa ⭐⭐⭐",
         "rooms": ["đơn", "đôi", "standard", "deluxe"], "price": "800k–3tr/đêm",
         "phone": "+84 214 3871 055", "email": "info@saparelaxhotel.com",
         "website": "https://www.saparelaxhotel.com"},
    ],
    "phú quốc": [
        {"id": 1, "name": "InterContinental Phú Quốc Long Beach ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "villa", "deluxe", "gia đình"], "price": "8–50tr/đêm",
         "phone": "+84 297 398 8888", "email": "reservations.phuquoc@ihg.com",
         "website": "https://phuquoc.intercontinental.com"},
        {"id": 2, "name": "JW Marriott Phú Quốc Emerald Bay ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "villa", "deluxe"], "price": "10–60tr/đêm",
         "phone": "+84 297 377 9999", "email": "jwphuquoc@marriott.com",
         "website": "https://www.marriott.com/phuquoc"},
        {"id": 3, "name": "Salinda Resort Phú Quốc ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "bungalow", "gia đình"], "price": "5–20tr/đêm",
         "phone": "+84 297 399 5888", "email": "reservations@salindaresort.com",
         "website": "https://www.salindaresort.com"},
    ],
    "bangkok": [
        {"id": 1, "name": "Mandarin Oriental Bangkok ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "deluxe", "gia đình"], "price": "$300–1500/đêm",
         "phone": "+66 2 659 9000", "email": "mobkk-reservations@mohg.com",
         "website": "https://www.mandarinoriental.com/bangkok"},
        {"id": 2, "name": "The Peninsula Bangkok ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe", "twin"], "price": "$250–800/đêm",
         "phone": "+66 2 020 2888", "email": "pbk@peninsula.com",
         "website": "https://www.peninsula.com/bangkok"},
        {"id": 3, "name": "Avani Riverside Bangkok ⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "standard"], "price": "$80–300/đêm",
         "phone": "+66 2 431 9100", "email": "avaniriverside@avanihotels.com",
         "website": "https://www.avanihotels.com/bangkok-riverside"},
    ],
    "tokyo": [
        {"id": 1, "name": "Aman Tokyo ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "deluxe"], "price": "¥100,000–500,000/đêm",
         "phone": "+81 3 5224 3333", "email": "tokyo@aman.com",
         "website": "https://www.aman.com/resorts/aman-tokyo"},
        {"id": 2, "name": "Park Hyatt Tokyo ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe", "twin"], "price": "¥60,000–200,000/đêm",
         "phone": "+81 3 5322 1234", "email": "tokyo.park@hyatt.com",
         "website": "https://www.hyatt.com/park-hyatt/tokyph"},
        {"id": 3, "name": "Keio Plaza Hotel Tokyo ⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "twin", "standard", "deluxe"], "price": "¥20,000–80,000/đêm",
         "phone": "+81 3 3344 0111", "email": "stay@keioplaza.co.jp",
         "website": "https://www.keioplaza.com"},
    ],
    "paris": [
        {"id": 1, "name": "Hôtel Ritz Paris ⭐⭐⭐⭐⭐",
         "rooms": ["đôi", "suite", "deluxe", "villa"], "price": "€800–5000/đêm",
         "phone": "+33 1 43 16 30 30", "email": "resa@ritzparis.com",
         "website": "https://www.ritzparis.com"},
        {"id": 2, "name": "Four Seasons Hotel George V Paris ⭐⭐⭐⭐⭐",
         "rooms": ["đơn", "đôi", "suite", "deluxe", "gia đình"], "price": "€700–3000/đêm",
         "phone": "+33 1 49 52 70 00", "email": "parisgv.reservations@fourseasons.com",
         "website": "https://www.fourseasons.com/paris"},
        {"id": 3, "name": "Citadines Apart'hotel Paris ⭐⭐⭐",
         "rooms": ["đơn", "đôi", "standard", "gia đình"], "price": "€80–250/đêm",
         "phone": "+33 1 56 77 57 57", "email": "paris@citadines.com",
         "website": "https://www.citadines.com/paris"},
    ],
}

ROOM_TYPE_MAP: Dict[str, str] = {
    "đơn": "Phòng đơn (Single)",
    "single": "Phòng đơn (Single)",
    "đôi": "Phòng đôi (Double)",
    "double": "Phòng đôi (Double)",
    "twin": "Phòng Twin (2 giường đơn)",
    "suite": "Phòng Suite",
    "gia đình": "Phòng gia đình (Family)",
    "family": "Phòng gia đình (Family)",
    "deluxe": "Phòng Deluxe",
    "standard": "Phòng Standard",
    "villa": "Villa / Bungalow",
    "bungalow": "Villa / Bungalow",
    "vip": "Phòng Suite",
}

BOOKING_INTENT_KWS = [
    "đặt phòng", "dat phong", "book phòng", "book phong",
    "đặt khách sạn", "dat khach san", "book hotel",
    "muốn đặt", "muon dat", "book room", "thuê phòng", "thue phong",
    "đặt room",
]

# Markers embedded in bot messages to track booking state
_MARKER_ASK_ROOM = "🛏️ **Bạn muốn đặt loại phòng"
_MARKER_ASK_INFO = "📋 **Thông tin đặt phòng**"


def _is_booking_intent(msg: str) -> bool:
    return any(k in msg for k in BOOKING_INTENT_KWS)


def _get_booking_state(history: List[Dict[str, str]]) -> Optional[str]:
    """Detect which step of the booking flow we're in from last bot message."""
    for msg in reversed(history):
        if msg["role"] == "assistant":
            content = msg["content"]
            if _MARKER_ASK_ROOM in content:
                return "waiting_room_type"
            if _MARKER_ASK_INFO in content:
                return "waiting_booking_info"
            break
    return None


def _extract_room_type_key(text: str) -> Optional[str]:
    """Return canonical room type key or None."""
    t = text.lower()
    # Number shortcuts: 1=đơn, 2=đôi, 3=twin, 4=suite, 5=deluxe, 6=gia đình, 7=villa
    number_map = {"1": "đơn", "2": "đôi", "3": "twin", "4": "suite",
                  "5": "deluxe", "6": "gia đình", "7": "villa"}
    m = re.search(r"^\s*([1-7])\s*$", t.strip())
    if m:
        return number_map.get(m.group(1))
    for key in ROOM_TYPE_MAP:
        if key in t:
            return key
    return None


def _find_hotels(city: str, room_key: Optional[str]) -> List[Dict]:
    hotels = HOTEL_ROOMS_DB.get(city, [])
    if not room_key:
        return hotels
    matched = [h for h in hotels if any(room_key in r or r in room_key for r in h["rooms"])]
    return matched if matched else hotels  # fallback: all hotels


def _format_hotel_list_for_booking(hotels: List[Dict], city: str, room_key: Optional[str]) -> str:
    room_display = ROOM_TYPE_MAP.get(room_key, room_key.title()) if room_key else "tất cả loại"
    lines = [f"🏨 **Khách sạn tại {city.title()} có {room_display}:**\n"]
    for h in hotels[:6]:
        lines.append(
            f"**{h['id']}. {h['name']}**\n"
            f"   💰 {h['price']} · 📞 {h['phone']}\n"
            f"   ✉️ {h['email']}\n"
        )
    lines.append(
        "\n📋 **Thông tin đặt phòng**\n"
        "Vui lòng điền và gửi lại *(Họ tên, SĐT, Email là **bắt buộc** — CSKH sẽ liên hệ lại)*:\n\n"
        "```\n"
        "Chọn số KS   : \n"
        "Họ tên       : \n"
        "Số điện thoại: \n"
        "Email        : \n"
        "Check-in     : (dd/mm/yyyy)\n"
        "Check-out    : (dd/mm/yyyy)\n"
        "Số khách     : \n"
        "Ghi chú      : \n"
        "```"
    )
    return "\n".join(lines)


def _parse_booking_info(msg: str, hotels: List[Dict]) -> Dict:
    info: Dict = {}

    # Hotel selection by number
    m = re.search(r"chọn\s*số\s*ks\s*[:\-]?\s*(\d+)", msg, re.IGNORECASE)
    if not m:
        m = re.search(r"^\s*(\d+)\s*$", msg.strip(), re.MULTILINE)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(hotels):
            info["hotel"] = hotels[idx]
    # Hotel by name substring
    if "hotel" not in info:
        for h in hotels:
            clean_name = h["name"].split("⭐")[0].strip().lower()
            if clean_name in msg.lower() or msg.lower() in clean_name:
                info["hotel"] = h
                break
    if "hotel" not in info and hotels:
        info["hotel"] = hotels[0]

    # Guest name
    m = re.search(r"họ tên\s*[:\-]\s*(.+)", msg, re.IGNORECASE)
    if m:
        info["guest_name"] = m.group(1).strip()

    # Phone
    m = re.search(r"(?:số điện thoại|điện thoại|phone|sdt)\s*[:\-]\s*([\d\s\+\-]{8,15})", msg, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(0\d{9,10}|\+84\d{9,10})\b", msg)
    if m:
        info["phone"] = m.group(1).strip()

    # Email
    m = re.search(r"[\w.\-]+@[\w.\-]+\.\w+", msg)
    if m:
        info["email"] = m.group(0)

    # Dates – look for labeled lines first
    ci = re.search(r"check.?in\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?)", msg, re.IGNORECASE)
    co = re.search(r"check.?out\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?)", msg, re.IGNORECASE)
    if ci:
        info["checkin"] = ci.group(1)
    if co:
        info["checkout"] = co.group(1)
    # Fallback: grab two bare dates in order
    if "checkin" not in info or "checkout" not in info:
        dates = re.findall(r"\b(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)\b", msg)
        if len(dates) >= 1 and "checkin" not in info:
            info["checkin"] = dates[0]
        if len(dates) >= 2 and "checkout" not in info:
            info["checkout"] = dates[1]

    # Num guests
    m = re.search(r"(?:số khách|khách|người|nguoi|guest)\s*[:\-]?\s*(\d+)", msg, re.IGNORECASE)
    if m:
        info["num_guests"] = int(m.group(1))

    # Notes
    m = re.search(r"(?:ghi chú|note|notes)\s*[:\-]\s*(.+)", msg, re.IGNORECASE)
    if m:
        info["notes"] = m.group(1).strip()

    return info


def _handle_booking(user_message: str, history: List[Dict[str, str]]) -> Optional[str]:
    """
    Multi-step booking flow.
    Step 1 (init):         detect booking intent → ask room type
    Step 2 (room type):    user picks room → show hotels + ask info form
    Step 3 (info):         user fills form → save to DB → confirmation
    """
    msg_norm = _normalize(user_message)
    state = _get_booking_state(history)

    # ── Step 1: booking intent detected ──────────────────────────────────────
    if state is None and _is_booking_intent(msg_norm):
        city = _extract_city_from_history(history)
        city_text = f" tại **{city.title()}**" if city else ""
        return (
            f"{_MARKER_ASK_ROOM} gì{city_text}?**\n\n"
            "Chọn loại phòng:\n"
            "1. 🛏️ Phòng đơn (Single)\n"
            "2. 🛏🛏 Phòng đôi (Double)\n"
            "3. 🛏🛏 Phòng Twin (2 giường đơn)\n"
            "4. 👑 Phòng Suite (cao cấp)\n"
            "5. 🌟 Phòng Deluxe\n"
            "6. 👨‍👩‍👧 Phòng Gia đình (Family)\n"
            "7. 🏡 Villa / Bungalow\n\n"
            "*(Gõ số thứ tự hoặc tên loại phòng)*"
        )

    # ── Step 2: user replied with room type ──────────────────────────────────
    if state == "waiting_room_type":
        city = _extract_city_from_history(history)
        # Also check current message for city
        if not city:
            for kw, c in KEYWORD_MAP.items():
                if kw in msg_norm:
                    city = c
                    break
        if not city:
            return (
                "Bạn muốn đặt phòng ở **thành phố nào**?\n\n"
                "Tôi có danh sách tại: Hà Nội, Đà Nẵng, Hội An, Sapa, Phú Quốc, Bangkok, Tokyo, Paris."
            )
        room_key = _extract_room_type_key(user_message)
        hotels = _find_hotels(city, room_key)
        return _format_hotel_list_for_booking(hotels, city, room_key)

    # ── Step 3: user filled booking info ─────────────────────────────────────
    if state == "waiting_booking_info":
        city = _extract_city_from_history(history)
        hotels_in_city = HOTEL_ROOMS_DB.get(city or "", [])

        # Also try to get room type from the bot message that showed hotels
        room_key = None
        for m in reversed(history):
            if m["role"] == "assistant" and _MARKER_ASK_INFO in m["content"]:
                room_key = _extract_room_type_key(m["content"])
                break

        info = _parse_booking_info(user_message, hotels_in_city)
        hotel = info.get("hotel", hotels_in_city[0] if hotels_in_city else {})

        missing = _vp_contact_missing(info)
        if missing:
            return (
                f"⚠️ Còn thiếu: **{', '.join(missing)}**.\n\n"
                "📋 **Thông tin đặt phòng** *(bắt buộc: Họ tên, SĐT, Email)*\n\n"
                "```\n"
                "Chọn số KS   : \n"
                "Họ tên       : \n"
                "Số điện thoại: \n"
                "Email        : \n"
                "Check-in     : (dd/mm/yyyy)\n"
                "Check-out    : (dd/mm/yyyy)\n"
                "Số khách     : \n"
                "Ghi chú      : \n"
                "```"
            )

        booking_data = {
            "city": city or "",
            "hotel_name": hotel.get("name", "").split("⭐")[0].strip(),
            "room_type": ROOM_TYPE_MAP.get(room_key, room_key or "Không xác định"),
            "guest_name": info.get("guest_name", ""),
            "phone": info.get("phone", ""),
            "email": info.get("email", ""),
            "checkin": info.get("checkin", ""),
            "checkout": info.get("checkout", ""),
            "num_guests": info.get("num_guests", 1),
            "notes": info.get("notes", ""),
        }
        booking_id, telegram_ok = _save_booking_and_notify(booking_data)
        id_label = f"`#{booking_id:04d}`" if booking_id else "`#---`"

        hotel_phone = hotel.get("phone", "N/A")
        hotel_email = hotel.get("email", "N/A")
        hotel_web = hotel.get("website", "")
        hotel_name_clean = hotel.get("name", "Khách sạn đã chọn").split("⭐")[0].strip()

        return (
            f"✅ **Yêu cầu đặt phòng đã được ghi nhận!**\n\n"
            f"📌 **Mã booking:** {id_label}\n\n"
            f"**Chi tiết:**\n"
            f"- 🏨 Khách sạn: **{hotel_name_clean}**\n"
            f"- 🛏️ Loại phòng: {booking_data['room_type']}\n"
            f"- 👤 Họ tên: {booking_data['guest_name']}\n"
            f"- 📞 SĐT: {booking_data['phone']}\n"
            f"- ✉️ Email: {booking_data['email']}\n"
            f"- 📅 Check-in: {booking_data['checkin'] or '*(chưa xác định)*'}\n"
            f"- 📅 Check-out: {booking_data['checkout'] or '*(chưa xác định)*'}\n"
            f"- 👥 Số khách: {booking_data['num_guests']}\n\n"
            f"**📬 Liên hệ khách sạn để xác nhận:**\n"
            f"- 📞 {hotel_phone}\n"
            f"- ✉️ {hotel_email}\n"
            + (f"- 🌐 [{hotel_web.replace('https://','').split('/')[0]}]({hotel_web})\n" if hotel_web else "")
            + (
                "\n📲 Đã gửi thông báo tới CSKH qua Telegram.\n"
                if telegram_ok
                else "\nℹ️ *(Telegram chưa cấu hình — chỉ lưu vào hệ thống)*\n"
            )
            + f"\n💡 *Trạng thái: **Chờ xác nhận** — Nhân viên sẽ liên hệ trong vòng 24h.*"
        )

    return None


# ===========================================================================
# VINPEARL PHÚ QUỐC — PLANNING FLOW (3-question → 2N1Đ timeline)
# ===========================================================================

VINPEARL_ROOMS: List[Dict] = [
    {
        "id": "vp1",
        "resort": "Vinpearl Resort & Spa Phú Quốc",
        "area": "Bãi Dài",
        "type": "Deluxe Ocean View",
        "price_range": "3.5–5 tr/đêm",
        "for_who": ["couple", "family"],
        "style": ["biển"],
        "budget": ["trung"],
        "highlights": "view biển trực diện, bể bơi vô cực, gần trung tâm Dương Đông",
        "source_url": "https://vinpearl.com/vi/vinpearl-resort-spa-phu-quoc",
    },
    {
        "id": "vp2",
        "resort": "Vinpearl Resort & Spa Phú Quốc",
        "area": "Bãi Dài",
        "type": "Suite",
        "price_range": "7–12 tr/đêm",
        "for_who": ["couple", "family"],
        "style": ["biển"],
        "budget": ["cao"],
        "highlights": "phòng khách riêng, view biển panorama, butler service",
        "source_url": "https://vinpearl.com/vi/vinpearl-resort-spa-phu-quoc",
    },
    {
        "id": "vp3",
        "resort": "Vinpearl Discovery Wonderworld Phú Quốc",
        "area": "Nam Phú Quốc",
        "type": "Standard Room",
        "price_range": "2.2–3.2 tr/đêm",
        "for_who": ["solo", "couple", "group"],
        "style": ["vui chơi"],
        "budget": ["thấp"],
        "highlights": "liền kề VinWonders, đi bộ đến park 5 phút, giá tốt nhất Vinpearl",
        "source_url": "https://vinpearl.com/vi/vinpearl-discovery-wonderworld-phu-quoc",
    },
    {
        "id": "vp4",
        "resort": "Vinpearl Discovery Wonderworld Phú Quốc",
        "area": "Nam Phú Quốc",
        "type": "Deluxe Room",
        "price_range": "3.5–5 tr/đêm",
        "for_who": ["couple", "family"],
        "style": ["vui chơi"],
        "budget": ["trung"],
        "highlights": "gần VinWonders và Safari nhất, bể bơi ngoài trời, view Grand World",
        "source_url": "https://vinpearl.com/vi/vinpearl-discovery-wonderworld-phu-quoc",
    },
    {
        "id": "vp5",
        "resort": "Vinpearl Golf Land Resort & Villas Phú Quốc",
        "area": "Bãi Dài",
        "type": "Pool Villa",
        "price_range": "12–25 tr/đêm",
        "for_who": ["couple", "family"],
        "style": ["biển", "vui chơi"],
        "budget": ["cao"],
        "highlights": "villa hồ bơi riêng, view sân golf và biển, sang trọng nhất Vinpearl",
        "source_url": "https://vinpearl.com/vi/vinpearl-golf-land-resort-villas-phu-quoc",
    },
    {
        "id": "vp6",
        "resort": "Vinpearl Resort & Golf Phú Quốc",
        "area": "Grand World",
        "type": "Deluxe Room",
        "price_range": "2.8–4.5 tr/đêm",
        "for_who": ["family", "group"],
        "style": ["vui chơi"],
        "budget": ["thấp", "trung"],
        "highlights": "trong khu Grand World, đi bộ ra phố đi bộ buổi tối, phù hợp đoàn đông",
        "source_url": "https://vinpearl.com/vi/vinpearl-resort-golf-phu-quoc",
    },
]

VINPEARL_DEALS: List[Dict] = [
    {
        "id": "deal1",
        "title": "Combo VinWonders + phòng giảm 20%",
        "discount": "20%",
        "condition": "Đặt combo phòng + vé VinWonders trên vinpearl.com",
        "for_rooms": ["vp3", "vp4", "vp6"],
        "style": ["vui chơi"],
        "source_url": "https://vinpearl.com/vi/khuyen-mai",
        "note": "Áp dụng khi đặt trực tuyến tại vinpearl.com, không kết hợp ưu đãi khác",
    },
    {
        "id": "deal2",
        "title": "Early bird — đặt trước 30 ngày giảm 15%",
        "discount": "15%",
        "condition": "Đặt và thanh toán trước ít nhất 30 ngày so với ngày nhận phòng",
        "for_rooms": ["vp1", "vp2", "vp5"],
        "style": ["biển"],
        "source_url": "https://vinpearl.com/vi/khuyen-mai",
        "note": "Chính sách không hoàn tiền khi huỷ phòng",
    },
    {
        "id": "deal3",
        "title": "Ưu đãi gia đình — trẻ em dưới 12 tuổi miễn phí ăn sáng",
        "discount": "Miễn phí ăn sáng cho trẻ em",
        "condition": "Đặt phòng gia đình tại Vinpearl Resort & Spa Phú Quốc",
        "for_rooms": ["vp1", "vp2"],
        "style": ["biển"],
        "source_url": "https://vinpearl.com/vi/khuyen-mai",
        "note": "Áp dụng tối đa 2 trẻ em dưới 12 tuổi / phòng",
    },
]

_VP_MARKER_Q1 = "🤝 **Câu 1/3"
_VP_MARKER_Q1_ONLY = "🤝 **Câu 1/3"   # alias kept for clarity
_VP_MARKER_Q2 = "💰 **Câu 2/3"
_VP_MARKER_Q2C = "💡 **Làm rõ ngân sách"
_VP_MARKER_Q3 = "🏖️ **Câu 3/3"
_VP_MARKER_Q3_FAST1 = "🏖️ **Câu 2/2"   # fast-track after Q1 (budget pre-known)
_VP_MARKER_Q3_FAST2 = "🏖️ **Câu 1/1"   # fast-track from initial (who + budget pre-known)
_VP_MARKER_RESULT = "📅 **Lịch trình Vinpearl"
_MARKER_VP_ASK_CONTACT = "📞 **Đăng ký liên hệ CSKH**"
_VP_MARKER_BOOKING_DONE = "✅ **Yêu cầu đặt lịch Vinpearl"

VP_BOOKING_INTENT_KWS = [
    "đặt lịch", "dat lich", "đặt chuyến", "dat chuyen",
    "xác nhận đặt", "xac nhan dat", "liên hệ đặt", "lien he dat",
    "đặt vinpearl", "dat vinpearl", "đặt tour", "dat tour",
    "đặt ngay", "dat ngay", "book trip", "muốn đặt", "muon dat",
    "đặt phòng vinpearl", "dat phong vinpearl",
]

# Map keyword → (destination_id, display_name) — all Vinpearl destinations in DB
_VP_DEST_MAP: Dict[str, tuple] = {
    "phú quốc": (1, "Phú Quốc"),
    "phu quoc": (1, "Phú Quốc"),
    "nha trang": (2, "Nha Trang"),
    "nam hội an": (3, "Nam Hội An"),
    "nam hoi an": (3, "Nam Hội An"),
    "hội an": (3, "Nam Hội An"),
    "hoi an": (3, "Nam Hội An"),
    "cửa hội": (4, "Cửa Hội"),
    "cua hoi": (4, "Cửa Hội"),
    "nghệ an": (4, "Cửa Hội"),
    "nghe an": (4, "Cửa Hội"),
    "hải phòng": (5, "Hải Phòng"),
    "hai phong": (5, "Hải Phòng"),
}

_VP_PLANNING_TRIGGERS = [
    "vinpearl", "vinwonders",
    "2n1đ", "2n1d", "2 ngày 1 đêm", "2 ngay 1 dem", "hai ngay mot dem",
] + list(_VP_DEST_MAP.keys())


def _is_vp_planning_intent(msg_norm: str) -> bool:
    return any(k in msg_norm for k in _VP_PLANNING_TRIGGERS)


def _detect_vp_dest(msg_norm: str) -> tuple:
    """Return (destination_id, display_name) for the destination mentioned. Default Phú Quốc."""
    for kw, info in _VP_DEST_MAP.items():
        if kw in msg_norm:
            return info
    return (1, "Phú Quốc")  # default


def _extract_trip_days(history: List[Dict], current_msg: str = "") -> int:
    """
    Extract number of trip days. Priority:
    1. Current user message
    2. Days embedded in Q1 assistant message (e.g. 'Chuyến đi: **5 ngày**')
    3. Any earlier user message containing days
    Default: 2 (2N1Đ).
    """
    # 1. Current message
    d = _extract_days(current_msg)
    if d and 1 <= d <= 14:
        return d

    # 2. Embedded in Q1 assistant message
    for msg in history:
        if msg["role"] == "assistant" and _VP_MARKER_Q1 in msg["content"]:
            m = re.search(r"Chuy[eêế]n đi.*?(\d+)\s*ngày", msg["content"])
            if m:
                d = int(m.group(1))
                if 1 <= d <= 14:
                    return d

    # 3. User messages
    for msg in history:
        if msg["role"] == "user":
            d = _extract_days(msg["content"])
            if d and 1 <= d <= 14:
                return d

    return 2


def _extract_dest_from_history(history: List[Dict]) -> tuple:
    """Extract (dest_id, dest_name) embedded in Q1 message. Default Phú Quốc."""
    for msg in history:
        if msg["role"] == "assistant" and _VP_MARKER_Q1 in msg["content"]:
            m = re.search(r"tại\s+\*\*([^*]+)\*\*", msg["content"])
            if m:
                dest_name = m.group(1).strip()
                for kw, info in _VP_DEST_MAP.items():
                    if kw in dest_name.lower():
                        return info
                # exact match by display name
                for info in _VP_DEST_MAP.values():
                    if info[1] == dest_name:
                        return info
    # fallback: scan user messages
    for msg in history:
        if msg["role"] == "user":
            dest_id, dest_name = _detect_vp_dest(_normalize(msg["content"]))
            if dest_id != 1 or "phú quốc" in msg["content"].lower() or "phu quoc" in msg["content"].lower():
                return (dest_id, dest_name)
    return (1, "Phú Quốc")


def _get_vp_state(history: List[Dict]) -> Optional[str]:
    for msg in reversed(history):
        if msg["role"] == "assistant":
            c = msg["content"]
            if _MARKER_VP_ASK_CONTACT in c:
                return "waiting_vp_contact"
            if _VP_MARKER_BOOKING_DONE in c:
                return "booking_done"
            # Full result (may also contain customize prompt at end)
            if _VP_MARKER_RESULT in c:
                return "result_shown"
            # Standalone customize-only message (no full result above)
            if _MARKER_VP_CUSTOMIZE in c:
                return "waiting_customize"
            if _VP_MARKER_Q3 in c or _VP_MARKER_Q3_FAST1 in c or _VP_MARKER_Q3_FAST2 in c:
                return "waiting_q3"
            if _VP_MARKER_Q2C in c:
                return "waiting_clarify"
            if _VP_MARKER_Q2 in c:
                return "waiting_q2"
            if _VP_MARKER_Q1 in c:
                return "waiting_q1"
            break
    return None


def _had_vp_itinerary(history: List[Dict]) -> bool:
    return any(
        m.get("role") == "assistant" and _VP_MARKER_RESULT in m.get("content", "")
        for m in history
    )


def _is_vp_booking_intent(msg: str, history: List[Dict]) -> bool:
    if not _had_vp_itinerary(history):
        return False
    if any(k in msg for k in VP_BOOKING_INTENT_KWS):
        return True
    if _is_booking_intent(msg):
        return True
    return False


def _extract_vp_booking_context(history: List[Dict]) -> Dict:
    """Lấy thông tin chuyến từ tin nhắn lịch trình gần nhất."""
    ctx: Dict = {"dest_name": "Phú Quốc", "room_type": "", "resort": "", "who": "couple", "budget": "trung"}
    for msg in reversed(history):
        if msg.get("role") != "assistant" or _VP_MARKER_RESULT not in msg.get("content", ""):
            continue
        c = msg["content"]
        m = re.search(r"Lịch trình Vinpearl\s+([^*\n]+?)\s+\d", c)
        if m:
            ctx["dest_name"] = m.group(1).strip()
        m = re.search(r"Phòng gợi ý:\*\*\s*(.+?)\s*—\s*(.+?)(?:\n|$)", c)
        if m:
            ctx["room_type"] = m.group(1).strip()
            ctx["resort"] = m.group(2).strip()
        break
    ctx["who"] = _extract_who_from_history(history)
    ctx["budget"] = _extract_budget_from_history_vp(history)
    ctx["days"] = _extract_trip_days(history)
    return ctx


def _parse_vp_contact_info(msg: str) -> Dict:
    info: Dict = {}

    # ── Labeled format (form filled in) ──────────────────────────────────────
    m = re.search(r"họ tên\s*[:\-]\s*([^\n,]+)", msg, re.IGNORECASE)
    if m:
        info["guest_name"] = m.group(1).strip()

    m = re.search(r"(?:số điện thoại|điện thoại|phone|sdt|tel)\s*[:\-]\s*([\d\s\+\-]{8,15})", msg, re.IGNORECASE)
    if not m:
        m = re.search(r"\b(0\d{9,10}|\+84\d{9,10})\b", msg)
    if m:
        info["phone"] = re.sub(r"\s+", "", m.group(1))

    m = re.search(r"email\s*[:\-]\s*([\w.\-]+@[\w.\-]+\.\w+)", msg, re.IGNORECASE)
    if not m:
        m = re.search(r"[\w.\-]+@[\w.\-]+\.\w+", msg)
    if m:
        info["email"] = m.group(1) if m.lastindex else m.group(0)

    ci = re.search(r"check.?in\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?)", msg, re.IGNORECASE)
    co = re.search(r"check.?out\s*[:\-]\s*(\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?)", msg, re.IGNORECASE)
    if ci:
        info["checkin"] = ci.group(1)
    if co:
        info["checkout"] = co.group(1)

    m = re.search(r"(?:số khách|khách|người)\s*[:\-]?\s*(\d+)", msg, re.IGNORECASE)
    if m:
        info["num_guests"] = int(m.group(1))

    m = re.search(r"(?:ghi chú|note)\s*[:\-]\s*(.+)", msg, re.IGNORECASE)
    if m:
        info["notes"] = m.group(1).strip()

    # ── Fallback: free-form / comma-separated (no labels) ────────────────────
    if not info.get("guest_name"):
        # Remove already-detected phone and email from text, then find the name
        clean = msg
        if info.get("phone"):
            clean = clean.replace(info["phone"], " ")
        if info.get("email"):
            clean = clean.replace(info["email"], " ")
        # Also strip loose phone/email patterns to avoid misidentification
        clean = re.sub(r"\b0\d{9,10}\b", " ", clean)
        clean = re.sub(r"\+84\d{9,10}\b", " ", clean)
        clean = re.sub(r"[\w.\-]+@[\w.\-]+\.\w+", " ", clean)
        clean = re.sub(r"\d{1,2}[\/\-\.]\d{1,2}(?:[\/\-\.]\d{2,4})?", " ", clean)  # dates
        # Split remaining by comma/newline/semicolon, take first non-trivial chunk
        parts = re.split(r"[,;\n]", clean)
        for part in parts:
            candidate = part.strip()
            # Must be ≥2 chars, mostly letters (Vietnamese name)
            if len(candidate) >= 2 and re.search(r"[A-Za-zÀ-ỹ]", candidate):
                # Reject obvious non-names (just digits, keywords, etc.)
                if not re.match(r"^\d+$", candidate):
                    info["guest_name"] = candidate
                    break

    return info


def _vp_contact_missing(info: Dict) -> List[str]:
    missing = []
    if not info.get("guest_name"):
        missing.append("Họ tên")
    if not info.get("phone"):
        missing.append("Số điện thoại")
    if not info.get("email"):
        missing.append("Email")
    return missing


def _format_vp_contact_form(ctx: Dict) -> str:
    dest = ctx.get("dest_name", "Vinpearl")
    room = ctx.get("room_type", "")
    resort = ctx.get("resort", "")
    room_line = f"**{room}** — {resort}\n" if room else ""
    return (
        f"{_MARKER_VP_ASK_CONTACT} — Vinpearl {dest}**\n\n"
        f"{room_line}"
        "Nhân viên chăm sóc khách hàng sẽ **gọi/email lại** để xác nhận đặt lịch.\n"
        "Vui lòng gửi **đủ 3 thông tin bắt buộc** (có thể thêm ngày đi nếu đã biết):\n\n"
        "```\n"
        "Họ tên       : \n"
        "Số điện thoại: \n"
        "Email        : \n"
        "Check-in     : (tùy chọn, dd/mm/yyyy)\n"
        "Check-out    : (tùy chọn)\n"
        "Số khách     : (tùy chọn)\n"
        "Ghi chú      : (tùy chọn)\n"
        "```"
    )


def _save_booking_and_notify(booking_data: Dict) -> tuple[Optional[int], bool]:
    booking_id = None
    telegram_ok = False
    try:
        from database import create_booking
        booking_id = create_booking(booking_data)
    except Exception as e:
        print(f"[DB] create_booking error: {e}")
    try:
        from services.telegram_notify import format_vp_booking_telegram, send_telegram_message
        telegram_ok = send_telegram_message(format_vp_booking_telegram(booking_data, booking_id))
    except Exception as e:
        print(f"[Telegram] notify error: {e}")
    return booking_id, telegram_ok


def _extract_who(text: str) -> str:
    t = text.lower()
    # Solo — check FIRST so "1 mình" doesn't accidentally match "1 người" couple check
    if any(k in t for k in [
        "một mình", "mot minh", "1 mình", "1minh", "di minh", "đi mình",
        "mình đi", "minh di", "solo", "1 người", "tui di", "tôi đi một",
        "chỉ mình", "chi minh", "mình thôi", "minh thoi",
    ]):
        return "solo"
    if any(k in t for k in ["gia đình", "gia dinh", "có con", "co con", "trẻ em", "tre em",
                              "bé", "ba mẹ", "bố mẹ", "bo me", "ba me", "cả nhà", "ca nha"]):
        return "family"
    if any(k in t for k in ["nhóm", "nhom", "bạn bè", "ban be", "hội", "team",
                              "3 người", "4 người", "5 người", "6 người"]):
        return "group"
    if any(k in t for k in ["cặp đôi", "cap doi", "vợ chồng", "vo chong",
                              "bạn trai", "ban trai", "bạn gái", "ban gai",
                              "người yêu", "nguoi yeu", "2 người", "hai người", "hai nguoi"]):
        return "couple"
    # Number shortcuts for Q1 menu (1=couple, 2=family, 3=group, 4=solo)
    stripped = t.strip()
    if stripped in ("1", "cặp", "cap"):
        return "couple"
    if stripped in ("2", "gia đình", "gia dinh"):
        return "family"
    if stripped in ("3", "nhóm", "nhom"):
        return "group"
    if stripped in ("4",):
        return "solo"
    return "couple"


def _who_label(who: str) -> str:
    return {"family": "gia đình", "group": "nhóm bạn", "couple": "cặp đôi", "solo": "một mình"}.get(who, who)


def _budget_label_vp(budget: str) -> str:
    return {
        "thấp": "thấp (dưới 3 tr/đêm)",
        "trung": "trung bình (3–6 tr/đêm)",
        "cao": "cao (trên 6 tr/đêm)",
    }.get(budget, budget)


def _room_fits_budget(price: float, budget: str) -> bool:
    if budget == "thấp":
        return price < 3_000_000
    if budget == "trung":
        return 3_000_000 <= price <= 6_000_000
    return price > 6_000_000


def _vp_party_size(who: str) -> tuple[int, int]:
    """(số người lớn, số trẻ em) dùng ước tính chi phí."""
    return {
        "solo": (1, 0),
        "couple": (2, 0),
        "family": (2, 2),
        "group": (4, 0),
    }.get(who, (2, 0))


def _estimate_vp_costs(
    budget: str,
    who: str,
    style: str,
    dest_id: int,
    days: int,
    nights: int,
    room_price_m: float,
    deal: Optional[Dict] = None,
) -> Dict:
    """
    Ước tính từng hạng mục (triệu VND) theo ngân sách + phong cách chuyến đi.
    Giá phụ trợ scale theo tier để tổng chi phí hợp lý với mức ngân sách phòng.
    """
    adults, children = _vp_party_size(who)
    eaters = adults + children

    # Values in k-VND (thousands). Convert to triệu = / 1_000.
    tiers = {
        "thấp": {"meal_k": 200, "vw_k": 550, "extra_k": 300, "transport_k": 200},
        "trung": {"meal_k": 400, "vw_k": 650, "extra_k": 400, "transport_k": 300},
        "cao": {"meal_k": 700, "vw_k": 900, "extra_k": 600, "transport_k": 450},
    }
    t = tiers.get(budget, tiers["trung"])

    room_cost = room_price_m * nights

    include_vw = style in ("vui chơi", "cả hai")
    include_extra = style in ("biển", "cả hai")

    def k_to_m(k_val: float) -> float:
        """Convert k-VND to triệu VND."""
        return k_val * 1_000 / 1_000_000  # = k_val / 1_000

    vw_cost = 0.0
    if include_vw:
        vw_cost = k_to_m(t["vw_k"]) * adults
        if children:
            vw_cost += k_to_m(t["vw_k"]) * 0.5 * children

    if dest_id == 2:
        extra_label = "🌊 Tour lặn san hô Hòn Mun"
        transport_note = "Cáp treo vào/ra đảo"
    else:
        extra_label = "🦁 Vé Vinpearl Safari"
        transport_note = "Di chuyển nội đảo"

    extra_cost = 0.0
    if include_extra:
        extra_cost = k_to_m(t["extra_k"]) * adults
        if children and who == "family":
            extra_cost += k_to_m(t["extra_k"]) * 0.5 * children

    meal_cost = k_to_m(t["meal_k"]) * eaters * days
    # transport: 1–2 trips/đảo/day, split by party
    transport_cost = k_to_m(t["transport_k"]) * max(1, (adults + max(0, children)) // 2 + 1)

    deal_discount = 0.0
    deal_pct_label = ""
    if deal:
        try:
            disc = deal.get("discount", "0%")
            pct = float(re.search(r"([\d.]+)", disc).group(1)) / 100
            deal_discount = room_cost * pct
            deal_pct_label = deal.get("discount", "")
        except Exception:
            pass

    total_lo = room_cost - deal_discount + vw_cost + extra_cost + meal_cost + transport_cost
    total_hi = total_lo * 1.08

    return {
        "room_cost": room_cost,
        "deal_discount": deal_discount,
        "deal_pct_label": deal_pct_label,
        "vw_cost": vw_cost,
        "extra_cost": extra_cost,
        "extra_label": extra_label,
        "meal_cost": meal_cost,
        "meal_note": f"~{t['meal_k']}k/người/ngày × {eaters} × {days} ngày",
        "transport_cost": transport_cost,
        "transport_note": transport_note,
        "total_lo": total_lo,
        "total_hi": total_hi,
        "adults": adults,
        "children": children,
        "include_vw": include_vw,
        "include_extra": include_extra,
        "tier_label": _budget_label_vp(budget),
    }


def _per_night_val_from_total(total_m: float, days: int) -> float:
    """Convert total trip budget (triệu) to per-night budget."""
    nights = max(1, days - 1) if days > 1 else 1
    return total_m / nights


def _val_to_budget_tier(val_m: float) -> str:
    if val_m >= 6:
        return "cao"
    if val_m >= 3:
        return "trung"
    if val_m > 0:
        return "thấp"
    return "mơ hồ"


def _extract_budget_vp(text: str, days: int = 2) -> str:
    """
    Extract budget tier from free text.
    Handles:
    - Keyword hints (cao/sang/luxury, thấp/tiết kiệm, trung)
    - Per-night amount: "5 triệu/đêm", "5tr/đêm"
    - Total trip amount: "20 triệu" (tổng) → chia cho số đêm
    - Menu shortcuts: "1" / "2" / "3"
    """
    t = text.lower()
    nights = max(1, days - 1) if days > 1 else 1

    if any(k in t for k in ["tùy", "tuy ", "chưa biết", "chua biet", "không biết", "oke", "okay",
                              "được hết", "thoải mái", "thoai mai", "bất kỳ", "bat ky"]):
        return "mơ hồ"

    if any(k in t for k in ["cao", "sang", "luxury", "vip", "không giới hạn", "nhiều tiền",
                              "trên 6", "tren 6"]):
        return "cao"
    if any(k in t for k in ["ít tiền", "it tien", "tiết kiệm", "tiet kiem", "rẻ",
                              "thấp", "thap", "dưới 3", "duoi 3"]):
        return "thấp"
    if any(k in t for k in ["trung", "vừa", "vua ", "bình thường", "tầm trung", "tam trung",
                              "tầm 4", "tam 4", "tầm 5", "tam 5", "3-6", "3 đến 6"]):
        return "trung"

    # Per-night explicit: "5tr/đêm" or "5 triệu mỗi đêm"
    per_night_m = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:tr|triệu|million)\s*(?:/\s*(?:đêm|dem)|mỗi\s*(?:đêm|dem)|một\s*(?:đêm|dem))",
        t,
    )
    if per_night_m:
        return _val_to_budget_tier(float(per_night_m.group(1)))

    # Total budget expressed in triệu — if "tổng" keyword or amount looks like total
    total_kw = any(k in t for k in ["tổng", "tong", "cả chuyến", "ca chuyen", "toàn bộ", "toan bo",
                                      "cho chuyến", "cho chuyen", "cho trip", "budget tổng"])
    all_amounts = re.findall(r"(\d+(?:\.\d+)?)\s*(?:triệu|tr|million|m\b)", t)
    if not all_amounts:
        all_amounts = re.findall(r"(\d+)\s*(?:trieu|million)", t)

    if all_amounts:
        largest = max(float(v) for v in all_amounts)
        # Heuristic: if amount > 8M and no explicit /đêm → treat as total trip budget
        is_total = total_kw or (largest > 8 and "/đêm" not in t and "mỗi đêm" not in t and "mot dem" not in t)
        if is_total and nights > 1:
            per_night = _per_night_val_from_total(largest, days)
            return _val_to_budget_tier(per_night)
        return _val_to_budget_tier(largest)

    stripped = t.strip()
    if stripped == "1":
        return "thấp"
    if stripped == "2":
        return "trung"
    if stripped == "3":
        return "cao"
    return "mơ hồ"


def _extract_vp_style(text: str) -> str:
    t = text.lower().strip()
    m = re.match(r"^\s*([123])\s*$", t)
    if m:
        return {"1": "biển", "2": "vui chơi", "3": "cả hai"}[m.group(1)]
    has_beach = any(k in t for k in ["biển", "bien", "beach", "tắm", "bơi", "resort", "nghỉ dưỡng", "nghi duong"])
    has_fun = any(k in t for k in ["vui chơi", "vui choi", "vinwonders", "safari", "giải trí", "trò chơi",
                                    "giai tri", "tro choi", "công viên", "cong vien", "theme park"])
    if (has_beach and has_fun) or any(k in t for k in ["cả hai", "ca hai", "đều", "deu"]):
        return "cả hai"
    if has_fun:
        return "vui chơi"
    if has_beach:
        return "biển"
    return "biển"


def _extract_who_from_history(history: List[Dict]) -> str:
    _who_reverse = {"gia đình": "family", "nhóm bạn": "group",
                    "cặp đôi": "couple", "một mình": "solo"}
    # Fast-track: who embedded as "👤*(đi với: ...)*" in any assistant message
    for msg in history:
        if msg["role"] == "assistant":
            c = msg.get("content", "")
            m = re.search(r"👤\*\(đi với:\s*([^)]+)\)", c)
            if m:
                label = m.group(1).strip()
                return _who_reverse.get(label, "couple")
    # Standard: answer after Q1 message
    found_q1 = False
    for msg in history:
        if not found_q1:
            if msg["role"] == "assistant" and _VP_MARKER_Q1 in msg["content"]:
                found_q1 = True
        else:
            if msg["role"] == "user":
                return _extract_who(_normalize(msg["content"]))
    # Last resort: check first user message for explicit who keyword
    for msg in history:
        if msg["role"] == "user":
            who = _extract_who(_normalize(msg["content"]))
            _who_explicit_kws = [
                "gia đình", "gia dinh", "nhóm", "nhom", "bạn bè",
                "cặp đôi", "cap doi", "vợ chồng", "bạn trai", "bạn gái", "người yêu",
                "một mình", "mot minh", "1 mình", "di minh", "mình đi", "solo",
            ]
            if any(k in _normalize(msg["content"]) for k in _who_explicit_kws):
                return who
            break
    return "couple"


_VP_BUDGET_EMBED_MARKER = "💰*(ngân sách:"


def _extract_budget_from_history_vp(history: List[Dict]) -> str:
    """
    Extract budget tier from history.
    Priority:
    1. User answer after Q2/Clarify marker
    2. Budget embedded in Q1 message (fast-track, already known from initial msg)
    3. First user message that has explicit budget info (initial trigger msg)
    """
    days = _extract_trip_days(history)

    # 1. Standard Q2 answer
    last_q2_idx = None
    for i, msg in enumerate(history):
        if msg["role"] == "assistant" and (_VP_MARKER_Q2 in msg["content"] or _VP_MARKER_Q2C in msg["content"]):
            last_q2_idx = i
    if last_q2_idx is not None:
        for i in range(last_q2_idx + 1, len(history)):
            if history[i]["role"] == "user":
                b = _extract_budget_vp(_normalize(history[i]["content"]), days)
                return b if b != "mơ hồ" else "trung"

    # 2. Budget embedded in Q1 marker (fast-track path)
    for msg in history:
        if msg["role"] == "assistant" and _VP_MARKER_Q1 in msg["content"]:
            m = re.search(r"💰\*\(ngân sách:\s*([^)]+)\)", msg["content"])
            if m:
                embedded = m.group(1).strip()
                if embedded in ("thấp", "trung", "cao"):
                    return embedded

    # 3. Scan earliest user message for budget info (the initial trigger message)
    for msg in history:
        if msg["role"] == "user":
            b = _extract_budget_vp(_normalize(msg["content"]), days)
            if b != "mơ hồ":
                return b
            break  # only check first user message here

    return "trung"


def _normalize_db_room(row: Dict) -> Dict:
    """Convert a DB vp_room row into the format _build_vp_timeline() expects."""
    price = row.get("price_per_night", 0)
    price_str = f"{price / 1_000_000:.1f} tr/đêm"
    addr = row.get("address", "")
    area = addr.split(",")[0].strip() if addr else row.get("resort_type", "")
    return {
        "_resort_id": row.get("resort_id"),   # kept for deal lookup
        "_price_per_night": price,
        "resort": row.get("resort_name", ""),
        "area": area,
        "type": row.get("name", ""),
        "price_range": price_str,
        "highlights": row.get("highlights", ""),
        "source_url": row.get("source_url", "https://vinpearl.com/vi/khuyen-mai"),
    }


def _normalize_db_deal(row: Dict) -> Dict:
    """Convert a DB vp_promotion row into the format _build_vp_timeline() expects."""
    dtype = row.get("discount_type", "percentage")
    dval = row.get("discount_value", 0)
    if dtype == "percentage":
        discount_str = f"{int(dval)}%"
    elif dtype == "fixed_amount":
        discount_str = f"{int(dval):,} VND/đêm"
    elif dtype in ("free_night", "combo"):
        discount_str = f"Combo giảm {int(dval)}%" if dtype == "combo" else f"Tặng {int(dval)} đêm miễn phí"
    else:
        discount_str = str(dval)
    return {
        "title": row.get("name", ""),
        "discount": discount_str,
        "condition": row.get("conditions", ""),
        "source_url": row.get("source_url", "https://vinpearl.com/vi/khuyen-mai"),
        "note": "",
    }


def _score_hardcoded_vp_room(room: Dict, who: str, budget: str, style: str) -> float:
    styles_to_check = ["biển", "vui chơi"] if style == "cả hai" else [style]
    style_match = any(s in room["style"] for s in styles_to_check)
    budget_match = budget in room["budget"]
    who_match = who in room["for_who"]
    score = (8.0 if style_match else 0.0) + (6.0 if budget_match else 0.0) + (10.0 if who_match else 0.0)
    if not style_match:
        score -= 5.0
    return score


def _find_vp_room(who: str, budget: str, style: str, dest_id: int = 1) -> Dict:
    """Fetch best matching room from DB for the given destination. Falls back to hardcoded."""
    try:
        from database import get_vp_rooms
        rows = get_vp_rooms(dest_id, who, budget, style)
        if rows:
            return _normalize_db_room(rows[0])
    except Exception as e:
        print(f"[DB] get_vp_rooms error: {e}")

    # Fallback: hardcoded list (Phú Quốc only)
    styles_to_check = ["biển", "vui chơi"] if style == "cả hai" else [style]
    candidates = [
        (_score_hardcoded_vp_room(room, who, budget, style), room)
        for room in VINPEARL_ROOMS
        if any(s in room["style"] for s in styles_to_check)
    ]
    if not candidates:
        candidates = [(1, r) for r in VINPEARL_ROOMS]
    if not candidates:
        return VINPEARL_ROOMS[0]
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def _find_vp_deal(room: Dict, dest_id: int = 1) -> Optional[Dict]:
    """Fetch active promotion for the room's resort from DB. Returns None if none found."""
    resort_id = room.get("_resort_id")
    if resort_id is not None:
        try:
            from database import get_vp_promotions
            rows = get_vp_promotions(dest_id, resort_id)
            if rows:
                return _normalize_db_deal(rows[0])
            return None   # no active deal — caller will show "chưa có"
        except Exception as e:
            print(f"[DB] get_vp_promotions error: {e}")
            return None

    # Fallback: hardcoded
    for deal in VINPEARL_DEALS:
        if room.get("id") in deal.get("for_rooms", []):
            return deal
    return None


# Activity slots per style: list of (morning, afternoon, evening) per day
# Each slot supports {resort} placeholder in morning of day 1.

# ── Phú Quốc ──────────────────────────────────────────────────────────────────
_VP_ACTIVITIES: Dict[str, list] = {
    "biển": [
        (
            "Check-in {resort}, nhận phòng, nghỉ ngơi",
            "Tắm biển **Bãi Dài**, bể bơi vô cực resort\n   *(Bãi Dài 20km — trong xanh, sóng nhỏ, đẹp nhất Phú Quốc)*",
            "Ăn hải sản tươi tại nhà hàng resort hoặc **Chợ đêm Dinh Cậu** (~20 phút)",
        ),
        (
            "Ăn sáng buffet resort, tắm biển buổi sáng",
            "**Làng chài Hàm Ninh** — ghẹ hấp, nhum biển, đặc sản thật giá bình dân *(cách 30 phút)*",
            "Nghỉ ngơi resort, thư giãn bể bơi",
        ),
        (
            "Bình minh **Bãi Sao** *(cát trắng mịn nhất Phú Quốc, cách ~35 phút taxi)*",
            "**Cáp treo Hòn Thơm** (8:00–17:30) — cáp treo 3 dây dài nhất thế giới 7,899m, view biển tuyệt đẹp",
            "Dạo **Dương Đông town**, mua đặc sản nước mắm, tiêu Phú Quốc",
        ),
        (
            "Spa half-day tại resort *(khách lưu trú giảm 20%)*",
            "Lặn ngắm san hô / snorkeling tại **Hòn Gầm Ghì** *(tour thuê qua resort, ~300k/người)*",
            "Ăn tối BBQ hải sản tươi tại resort",
        ),
        (
            "Tắm biển lần cuối, chụp ảnh lưu niệm",
            "Mua sắm đặc sản: nước mắm Phú Quốc, tiêu, nhum biển khô",
            "Ra **sân bay / cảng** *(kiểm tra giờ tàu/bay về)*",
        ),
    ],
    "vui chơi": [
        (
            "Check-in {resort}, nhận phòng",
            "**VinWonders Phú Quốc** (13:30–21:00)\n   💡 *Vào chiều: tránh nóng, tránh đông, đủ thời gian chơi hết khu*\n   ⚠️ *VinWonders + Safari KHÔNG nên cùng 1 ngày — Safari đóng 16:30*",
            "**Grand World** phố đi bộ, xem show ánh sáng (đến 22:00)",
        ),
        (
            "**Vinpearl Safari** *(vào sớm 8:30 — đóng 16:30)*\n   💡 *Xe buýt safari toàn khu ~2.5 giờ, đi sớm để xem đủ*",
            "Nghỉ ngơi bể bơi resort / spa",
            "**Chợ đêm Dinh Cậu** (~20 phút) — hải sản tươi, đồ lưu niệm",
        ),
        (
            "Tắm biển Bãi Dài, nghỉ ngơi buổi sáng",
            "**Cáp treo Hòn Thơm** (8:00–17:30) — cáp treo dài nhất thế giới, view biển panorama",
            "**Làng chài Hàm Ninh** — ghẹ hấp, nhum biển đặc sản",
        ),
        (
            "Spa half-day tại resort",
            "**Bãi Sao** — bãi biển đẹp nhất Phú Quốc *(cách 35 phút taxi)*",
            "**Dương Đông town** — mua nước mắm Phú Quốc, tiêu",
        ),
        (
            "Tắm biển lần cuối",
            "Mua sắm đặc sản Phú Quốc",
            "Ra **sân bay / cảng**",
        ),
    ],
    "cả hai": [
        (
            "Check-in {resort}, nhận phòng",
            "Tắm biển **Bãi Dài** *(sóng nhỏ, trong xanh)*",
            "Ăn hải sản hoặc **Chợ đêm Dinh Cậu** (~20 phút)",
        ),
        (
            "**VinWonders Phú Quốc** (8:30–13:00)\n   💡 *Vào sáng sớm — chơi 4–5 giờ thoải mái*",
            "**Làng chài Hàm Ninh** — ghẹ hấp đặc sản *(cách 30 phút)*",
            "Nghỉ ngơi resort",
        ),
        (
            "**Vinpearl Safari** *(vào sớm 8:30 — đóng 16:30)*",
            "Bể bơi resort, thư giãn",
            "**Grand World** phố đi bộ, xem show",
        ),
        (
            "Bình minh **Bãi Sao** *(cát trắng mịn nhất đảo)*",
            "**Cáp treo Hòn Thơm** (8:00–17:30) — cáp treo dài nhất thế giới",
            "**Dương Đông town** — mua đặc sản",
        ),
        (
            "Spa half-day tại resort / tắm biển lần cuối",
            "Mua sắm đặc sản Phú Quốc: nước mắm, tiêu, nhum khô",
            "Ra **sân bay / cảng** *(kiểm tra giờ tàu/bay)*",
        ),
    ],
}

# ── Nha Trang ─────────────────────────────────────────────────────────────────
_VP_ACTIVITIES_NT: Dict[str, list] = {
    "biển": [
        (
            "Check-in {resort} *(cáp treo từ bờ ra Đảo Hòn Tre — ~5 phút, view biển panorama)*",
            "Tắm biển riêng Đảo Hòn Tre, bể bơi ngoài trời resort",
            "Ăn hải sản tại nhà hàng resort hoặc **Phố đi bộ Trần Phú** *(cáp treo vào bờ ~5 phút)*",
        ),
        (
            "Ăn sáng buffet resort, tắm biển sáng sớm — biển calmer, ít người",
            "Tour **lặn ngắm san hô Hòn Mun** *(khu bảo tồn biển, đặt qua resort ~350k/người)*",
            "**Phố đêm Nha Trang** — bạch tuộc nướng, ốc hải sản tươi, cà phê view biển",
        ),
        (
            "Spa half-day tại resort *(Vinpearl Spa đảo Hòn Tre — gói 90 phút)*",
            "**Hòn Tằm** / snorkeling — đảo hoang sơ, nước trong xanh *(tour ~400k/người)*",
            "Dạo **Nha Trang city** — bánh căn, nem nướng, bún cá, mua đặc sản yến sào",
        ),
        (
            "Tắm biển lần cuối, chụp ảnh lưu niệm trên đảo",
            "Mua sắm đặc sản: **yến sào Nha Trang**, rong nho, mực khô, nước mắm",
            "Ra **sân bay Cam Ranh** *(cách trung tâm Nha Trang ~30 phút)*",
        ),
    ],
    "vui chơi": [
        (
            "Check-in {resort} *(cáp treo ra Đảo Hòn Tre, nhìn thấy toàn thành phố Nha Trang từ trên cao)*",
            "**VinWonders Nha Trang** *(ngay trên đảo Hòn Tre, đi bộ từ resort ~10 phút)*\n   💡 *Vào chiều: tránh nóng, chơi đến tối*",
            "Ăn tối resort hoặc **Phố đi bộ Trần Phú**",
        ),
        (
            "**VinWonders Nha Trang** tiếp — khu vui chơi trẻ em, tàu lượn, show nước\n   ⏰ *Mở cửa 9:00–22:00, đủ thời gian chơi 2 ngày*",
            "Bể bơi resort / spa thư giãn",
            "**Chợ Đầm Nha Trang** — hải sản khô, yến sào, mua sắm đặc sản",
        ),
        (
            "Tour **lặn ngắm san hô Hòn Mun** *(khu bảo tồn biển quốc gia)*",
            "Tắm biển resort, nghỉ ngơi",
            "**Phố đêm Nha Trang** — nem nướng, bánh căn, bún cá Nha Trang",
        ),
        (
            "Spa half-day tại resort",
            "Mua sắm đặc sản yến sào, rong nho, mực khô",
            "Ra **sân bay Cam Ranh** *(~30 phút từ trung tâm)*",
        ),
    ],
    "cả hai": [
        (
            "Check-in {resort} *(cáp treo ra Đảo Hòn Tre — 5 phút, view thành phố tuyệt đẹp)*",
            "Tắm biển riêng Hòn Tre, bể bơi resort",
            "**Phố đi bộ Trần Phú** — hải sản tươi, nem nướng Ninh Hoà",
        ),
        (
            "**VinWonders Nha Trang** (9:00–13:00) — khu vui chơi ngay trên đảo\n   💡 *Vào sáng — chơi 4 giờ thoải mái, tránh nắng chiều*",
            "Tour **lặn ngắm san hô Hòn Mun** *(~350k/người, đặt qua resort)*",
            "Ăn tối tại resort hoặc **Phố đêm Nha Trang**",
        ),
        (
            "Spa half-day / tắm biển buổi sáng",
            "**Hòn Tằm** — đảo hoang sơ, snorkeling *(tour ~400k/người)*",
            "**Chợ Đầm Nha Trang** — mua yến sào, rong nho, đặc sản biển",
        ),
        (
            "Tắm biển lần cuối, chụp ảnh lưu niệm",
            "Mua sắm: yến sào Khánh Hoà, rong nho tươi, mực một nắng",
            "Ra **sân bay Cam Ranh** *(~30 phút taxi/xe công nghệ)*",
        ),
    ],
}

# ── Map dest_id → activity dict (add more destinations here as needed) ─────────
_VP_ACTIVITIES_BY_DEST: Dict[int, Dict[str, list]] = {
    1: _VP_ACTIVITIES,       # Phú Quốc
    2: _VP_ACTIVITIES_NT,    # Nha Trang
    # 3: _VP_ACTIVITIES_NHA  # Nam Hội An (future)
}

_VP_EXTRA_DAY_BY_DEST: Dict[int, tuple] = {
    1: (  # Phú Quốc
        "Tự do khám phá — tắm biển, spa, hoặc thêm ngày thư giãn",
        "Lặn ngắm san hô, câu cá ngoài khơi, hoặc dạo đảo",
        "Ăn tối hải sản, nghỉ ngơi resort",
    ),
    2: (  # Nha Trang
        "Tự do — tắm biển Đảo Hòn Tre, spa, hoặc tour đảo thêm",
        "Kayak / paddleboard ven đảo, hoặc thêm buổi lặn biển",
        "Ăn tối hải sản Nha Trang, nghỉ ngơi resort",
    ),
    3: (  # Nam Hội An
        "Tự do — tắm biển An Bàng, hoặc đạp xe khám phá vùng quê",
        "Thăm phố cổ Hội An *(cách 35 phút)* — đèn lồng, bánh mì Phượng",
        "Mua sắm đặc sản lụa Hội An, về resort nghỉ ngơi",
    ),
}
_VP_EXTRA_DAY = _VP_EXTRA_DAY_BY_DEST[1]  # fallback Phú Quốc


_MARKER_VP_CUSTOMIZE = "🔧 **Tùy chỉnh lịch trình"


def _try_switch_room(msg_norm: str, all_rooms: List[Dict], who: str, budget: str, nights: int) -> Optional[Dict]:
    """
    Try to find a room switch request.
    Handles: "đổi sang phòng 3", "chọn phòng Family Deluxe", "phòng 2", number alone.
    Returns normalised room dict or None.
    """
    rooms_sorted = sorted(all_rooms, key=lambda r: r.get("price_per_night", 0))

    # Number-based: "phòng 2", "phong 2", then "đổi sang 2", "chon 3" etc.
    m = (
        re.search(r"(?:phòng|phong)\s+(\d+)", msg_norm, re.IGNORECASE)
        or re.search(r"(?:đổi|doi|chọn|chon|switch|chuyen|chuyển)\s+(?:sang\s+)?(?:phòng|phong\s+)?(\d+)\b", msg_norm, re.IGNORECASE)
        or re.search(r"\broom\s+(\d+)\b", msg_norm, re.IGNORECASE)
    )
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(rooms_sorted):
            return _normalize_db_room(rooms_sorted[idx])

    # Name-based: find partial match in room names (strip accents for comparison)
    import unicodedata

    def _strip(s: str) -> str:
        s = unicodedata.normalize("NFD", s.lower())
        return "".join(c for c in s if unicodedata.category(c) != "Mn")

    msg_strip = _strip(msg_norm)
    for r in all_rooms:
        nm_strip = _strip(r.get("name", ""))
        words = [w for w in nm_strip.split() if len(w) > 3]
        if words and sum(1 for w in words if w in msg_strip) >= min(2, len(words)):
            return _normalize_db_room(r)

    return None


def _try_extract_day_change(msg_norm: str, current_days: int) -> Optional[int]:
    """Return new day count from messages like 'thêm 1 ngày'/'them 1 ngay', 'rút còn 3 ngày', '7 ngày'."""
    # "thêm N ngày" / "them N ngay"
    m = re.search(r"(?:thêm|them)\s+(\d+)\s*(?:ngày|ngay)", msg_norm, re.IGNORECASE)
    if m:
        return min(14, current_days + int(m.group(1)))
    # "bớt N ngày", "rút N ngày", "bot/rut/giam"
    m = re.search(r"(?:bớt|bot|rút|rut|giảm|giam)\s+(\d+)\s*(?:ngày|ngay)", msg_norm, re.IGNORECASE)
    if m:
        return max(1, current_days - int(m.group(1)))
    # "N ngày"/"N ngay" with optional prefix
    m = re.search(r"(?:còn|con|sang|đổi|doi|thành|thanh)?\s*(\d+)\s*(?:ngày|ngay)", msg_norm, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        if 1 <= val <= 14 and val != current_days:
            return val
    return None


def _handle_activity_change_request(
    msg_norm: str, history: List[Dict],
    who: str, budget: str, days: int,
    dest_id: int, dest_name: str, all_rooms: List[Dict],
) -> str:
    """
    Detect which day + slot the user wants to change and regenerate timeline with override.
    Supports: "ngày N buổi sáng/chiều/tối đổi sang X"
    """
    day_m = re.search(r"(?:ngày|ngay)\s+(\d+)", msg_norm)
    slot_m = re.search(r"(sáng|sang|chiều|chieu|buổi sáng|buổi chiều|buoi sang|buoi chieu|tối|toi|buổi tối|buoi toi)", msg_norm)
    change_m = re.search(r"(?:đổi.*sang|doi.*sang|thay.*bằng|thay.*bang|thêm|them|thay)\s+(.+)", msg_norm)

    if not (day_m and change_m):
        return (
            f"{_MARKER_VP_CUSTOMIZE} — đổi hoạt động?**\n\n"
            "Tôi chưa hiểu rõ bạn muốn thay gì. Vui lòng mô tả theo dạng:\n\n"
            "**Ngày [số] buổi [sáng/chiều/tối] đổi sang [hoạt động mới]**\n\n"
            "Ví dụ: *'ngày 2 buổi chiều đổi sang tham quan Tháp Bà Ponagar'*"
        )

    day_num = int(day_m.group(1))
    slot_name = "chiều"
    if slot_m:
        raw = slot_m.group(1)
        if any(k in raw for k in ["sáng", "sang"]):
            slot_name = "sáng"
        elif any(k in raw for k in ["tối", "toi"]):
            slot_name = "tối"

    new_activity = change_m.group(1).strip()

    # Rebuild timeline with override
    who_label = _who_label(who)
    dest_activities = _VP_ACTIVITIES_BY_DEST.get(dest_id, _VP_ACTIVITIES)
    cur_style = "cả hai"
    for m_h in reversed(history):
        if m_h["role"] == "assistant" and _VP_MARKER_RESULT in m_h["content"]:
            c = m_h["content"]
            if "biển & nghỉ dưỡng" in c.lower():
                cur_style = "biển"
            elif "vui chơi" in c[:500].lower():
                cur_style = "vui chơi"
            break

    activity_pool = dest_activities.get(cur_style, dest_activities.get("biển", _VP_ACTIVITIES["biển"]))
    extra_day_template = _VP_EXTRA_DAY_BY_DEST.get(dest_id, _VP_EXTRA_DAY)
    nights = max(1, days - 1)

    # Find the recommended room from history
    rec_room = None
    for m_h in reversed(history):
        if m_h["role"] == "assistant" and _VP_MARKER_RESULT in m_h["content"]:
            bm = re.search(r"Phòng gợi ý:\*\*\s*(.+?)\s*—", m_h["content"])
            if bm and all_rooms:
                nm_search = bm.group(1).strip()
                for r in all_rooms:
                    if nm_search in r.get("name", ""):
                        rec_room = _normalize_db_room(r)
                        break
            break
    if not rec_room:
        rec_room = _find_vp_room(who, budget, cur_style, dest_id)

    day_blocks = []
    for i in range(days):
        if i < len(activity_pool):
            mor, aft, eve = activity_pool[i]
        else:
            mor, aft, eve = extra_day_template
        if i == 0:
            resort_name = rec_room.get("resort", "resort")
            mor = mor.replace("{resort}", resort_name)
        if i == days - 1 and "sân bay" not in eve and "cảng" not in eve:
            eve = "Ra **sân bay / cảng** *(kiểm tra giờ tàu/bay về)*"
        # Apply override
        if i + 1 == day_num:
            if slot_name == "sáng":
                mor = f"**{new_activity}** *(thay đổi theo yêu cầu)*"
            elif slot_name == "tối":
                eve = f"**{new_activity}** *(thay đổi theo yêu cầu)*"
            else:
                aft = f"**{new_activity}** *(thay đổi theo yêu cầu)*"
        day_blocks.append(
            f"**📌 Ngày {i + 1}**\n"
            f"- 🌅 Sáng: {mor}\n"
            f"- ☀️ Chiều: {aft}\n"
            f"- 🌙 Tối: {eve}"
        )

    label = f"{days}N{nights}Đ" if days > 1 else "1 ngày"
    timeline_str = "\n\n".join(day_blocks)
    customize_prompt = _build_customize_prompt()

    return (
        f"📅 **Lịch trình Vinpearl {dest_name} {label}** — {who_label}\n"
        f"*(Đã cập nhật: ngày {day_num} buổi {slot_name} → {new_activity})*\n\n"
        f"{timeline_str}\n\n"
        f"---\n"
        f"{customize_prompt}"
    )


def _build_rooms_comparison(
    all_rooms: Optional[List[Dict]],
    nights: int,
    budget: str,
    dest_name: str,
    recommended: Dict,
    who: str,
) -> str:
    """
    Build a compact markdown table comparing ≥5 rooms.
    Marks: ⭐ gợi ý | ✅ trong ngân sách | 💰 rẻ hơn | 💎 cao hơn
    """
    if not all_rooms:
        return ""

    rooms = sorted(all_rooms, key=lambda r: r.get("price_per_night", 0))
    display = rooms[:8]

    budget_note = _budget_label_vp(budget)
    rec_name = recommended.get("type", "") or recommended.get("name", "")

    tier_icon = {"mid": "💚", "luxury": "💎", "ultra": "👑"}

    header = (
        f"\n\n---\n### 🏨 So sánh {len(display)} loại phòng — Vinpearl {dest_name}\n\n"
        f"*(✅ trong ngân sách **{budget_note}** · ⭐ phòng được gợi ý)*\n\n"
        "| # | Phòng | Resort | Giá/đêm | Tổng | Phù hợp | Điểm nổi bật | |\n"
        "|:---:|---|---|---:|---:|---|---|:---:|\n"
    )

    rows = []
    for idx, r in enumerate(display, start=1):
        p     = float(r.get("price_per_night", 0))
        p_m   = p / 1_000_000
        p_tot = p_m * nights
        nm    = r.get("name", "")
        rn    = r.get("resort_name", "")
        suf   = r.get("suitable_for", "").replace("Gia đình có trẻ nhỏ", "👨‍👩‍👧 Gia đình").replace("Cặp đôi", "👫").replace("Solo", "🧍").replace("Nhóm bạn", "👥")
        hl    = r.get("highlights", "")
        lvl   = r.get("budget_level", "mid")
        bf    = "🍳" if r.get("breakfast_included") else ""
        src   = r.get("source_url", "https://vinpearl.com")

        is_rec    = nm == rec_name or nm in rec_name or rec_name in nm
        in_budget = _room_fits_budget(p, budget)

        if is_rec:
            badge = "⭐"
        elif in_budget:
            badge = "✅"
        elif p_m < {"thấp": 3.0, "trung": 3.0, "cao": 6.0}.get(budget, 3.0):
            badge = "💰"
        else:
            badge = "💎"

        tier = tier_icon.get(lvl, "")
        rows.append(
            f"| {idx} | **{nm}** {bf} | {rn} | {tier} {p_m:.1f} tr | {p_tot:.1f} tr | {suf} | {hl} | {badge} [🔗]({src}) |"
        )

    footer = (
        "\n\n> 💡 **Thay đổi phòng:** Gõ `đổi sang phòng 2` hoặc tên phòng bất kỳ."
    )
    return header + "\n".join(rows) + footer


def _build_customize_prompt() -> str:
    return (
        f"{_MARKER_VP_CUSTOMIZE}?**\n\n"
        "| # | Tuỳ chỉnh | Ví dụ |\n"
        "|:---:|---|---|\n"
        "| 1 | 🏨 Đổi loại phòng | `đổi sang phòng 2` hoặc tên phòng |\n"
        "| 2 | 📅 Thay đổi số ngày | `thêm 1 ngày` · `rút còn 3 ngày` |\n"
        "| 3 | 🌊 Thiên về biển & nghỉ dưỡng | `biển hơn` |\n"
        "| 4 | 🎢 Thiên về vui chơi | `vui chơi hơn` |\n"
        "| 5 | 🗺️ Đổi hoạt động cụ thể | `ngày 2 chiều đổi sang spa` |\n"
        "| 6 | ✅ Giữ nguyên & đặt lịch | `đặt lịch` |\n\n"
        "*(Hoặc mô tả tự do bất kỳ thay đổi nào bạn muốn)*"
    )


def _build_vp_timeline(who: str, style: str, room: Dict, deal: Optional[Dict], days: int = 2, dest_name: str = "Phú Quốc", dest_id: int = 1, all_rooms: Optional[List[Dict]] = None, budget: str = "trung") -> str:
    who_label = _who_label(who)
    days = max(1, min(days, 14))

    dest_activities = _VP_ACTIVITIES_BY_DEST.get(dest_id, _VP_ACTIVITIES)
    activity_pool = dest_activities.get(style, dest_activities.get("biển", _VP_ACTIVITIES["biển"]))
    resort_name = room.get("resort", "resort")

    extra_day_template = _VP_EXTRA_DAY_BY_DEST.get(dest_id, _VP_EXTRA_DAY)

    # ── Timeline table ─────────────────────────────────────────────────────────
    timeline_rows = []
    for i in range(days):
        if i < len(activity_pool):
            mor, aft, eve = activity_pool[i]
        else:
            mor, aft, eve = extra_day_template

        if i == 0:
            mor = mor.replace("{resort}", resort_name)

        if i == days - 1 and "sân bay" not in eve and "cảng" not in eve:
            eve = "Ra **sân bay / cảng** *(kiểm tra giờ tàu/bay về)*"

        timeline_rows.append(
            f"| **Ngày {i + 1}** | 🌅 {mor} | ☀️ {aft} | 🌙 {eve} |"
        )

    timeline_str = (
        "| Ngày | 🌅 Sáng | ☀️ Chiều | 🌙 Tối |\n"
        "|:---:|---|---|---|\n"
        + "\n".join(timeline_rows)
    )
    nights = days - 1 if days > 1 else 1
    label = f"{days}N{nights}Đ" if days > 1 else "1 ngày"

    # ── Chi phí ước tính theo từng mục ───────────────────────────────────────
    price_str = room.get("price_range", "")
    if room.get("_price_per_night"):
        price_val = float(room["_price_per_night"]) / 1_000_000
    else:
        try:
            price_val = float(re.search(r"([\d.]+)", price_str).group(1))
        except Exception:
            price_val = 0.0

    costs = _estimate_vp_costs(budget, who, style, dest_id, days, nights, price_val, deal)
    room_cost = costs["room_cost"]
    deal_discount = costs["deal_discount"]
    vw_cost = costs["vw_cost"]
    extra_cost = costs["extra_cost"]
    meal_cost = costs["meal_cost"]
    transport_cost = costs["transport_cost"]
    total_lo = costs["total_lo"]
    total_hi = costs["total_hi"]

    cost_rows = [
        f"| 🏨 Phòng {room['type']} × {nights} đêm | **{room_cost:.1f} tr** |",
    ]
    if deal and deal_discount > 0:
        cost_rows.append(f"| 🎁 Giảm giá ưu đãi ({deal['discount']}) | −{deal_discount:.1f} tr |")
    if costs["include_vw"] and vw_cost > 0:
        cost_rows.append(
            f"| 🎢 Vé VinWonders ({costs['adults']} NL"
            + (f" + {costs['children']} trẻ" if costs["children"] else "")
            + f", {costs['tier_label']}) | ~{vw_cost:.1f} tr |"
        )
    if costs["include_extra"] and extra_cost > 0:
        cost_rows.append(f"| {costs['extra_label']} | ~{extra_cost:.1f} tr |")
    cost_rows.append(f"| 🍽️ Ăn uống ({costs['meal_note']}) | ~{meal_cost:.1f} tr |")
    cost_rows.append(f"| 🚕 {costs['transport_note']} | ~{transport_cost:.1f} tr |")
    cost_rows.append(
        f"| **💰 Tổng ước tính** *(chưa gồm vé máy bay, theo ngân sách {costs['tier_label']})* "
        f"| **~{total_lo:.1f}–{total_hi:.1f} tr** |"
    )

    party_desc = f"{costs['adults']} người lớn"
    if costs["children"]:
        party_desc += f" + {costs['children']} trẻ em"

    # Budget overflow warning — when user stated a total budget
    budget_warning = ""
    if all_rooms and total_lo > 0:
        # Try to find if user stated a total budget in history (via our budget marker)
        # We can infer: if total exceeds the expected tier range, warn
        tier_max = {"thấp": 10.0, "trung": 25.0, "cao": 80.0}
        if total_lo > tier_max.get(budget, 25.0):
            alt_room_hint = ""
            if all_rooms:
                cheaper = [r for r in all_rooms if _room_fits_budget(float(r.get("price_per_night", 0)), budget)
                           and r.get("price_per_night", 0) < (room.get("_price_per_night") or float("inf"))]
                if cheaper:
                    c = cheaper[0]
                    budget_warning = (
                        f"\n\n⚠️ *Tổng chi phí ước tính ({total_lo:.1f} tr) có thể vượt kỳ vọng. "
                        f"Bạn cũng có thể chọn phòng rẻ hơn như **{c['name']}** "
                        f"({c['price_per_night']/1_000_000:.1f} tr/đêm) để tiết kiệm thêm.*"
                    )

    cost_table = (
        "| Hạng mục | Chi phí |\n"
        "|---|---|\n"
        + "\n".join(cost_rows)
        + f"\n\n*Ước tính cho {party_desc}. Các mục phụ thuộc theo phong cách chuyến đi và ngân sách bạn chọn.*"
        + budget_warning
    )

    budget_note = _budget_label_vp(budget)
    nightly = price_val * 1_000_000
    in_budget_tag = " ✅" if _room_fits_budget(nightly, budget) else ""

    # ── Room info table ────────────────────────────────────────────────────────
    deal_row = ""
    if deal:
        deal_row = (
            f"| 🎁 Ưu đãi | **{deal['title']}** — giảm {deal['discount']} · {deal['condition']} · [Xem]({deal['source_url']}) |\n"
        )
    else:
        deal_row = "| 🎁 Ưu đãi | Chưa có ưu đãi — [Xem tại đây](https://vinpearl.com/vi/khuyen-mai) |\n"

    room_table = (
        "| Thông tin | Chi tiết |\n"
        "|---|---|\n"
        f"| 🏨 Phòng gợi ý{in_budget_tag} | **{room['type']}** — {room['resort']} |\n"
        f"| 💰 Giá | {room['price_range']} × {nights} đêm = **{room_cost:.1f} tr** |\n"
        f"| 📍 Vị trí | {room['area']} |\n"
        f"| ✨ Điểm nổi bật | {room['highlights']} |\n"
        f"| 📊 Ngân sách | {budget_note}{in_budget_tag} |\n"
        f"| 🔗 Chi tiết | [Xem phòng]({room['source_url']}) |\n"
        + deal_row
    )

    # ── All rooms comparison block ──────────────────────────────────────────────
    all_rooms_block = _build_rooms_comparison(all_rooms, nights, budget, dest_name, room, who)

    customize_prompt = _build_customize_prompt()

    return (
        f"## 📅 Lịch trình Vinpearl {dest_name} {label} — {who_label}\n\n"
        f"{timeline_str}\n\n"
        f"---\n"
        f"### 🏨 Phòng & Ưu đãi\n\n"
        f"{room_table}\n"
        f"---\n"
        f"### 💵 Chi phí ước tính\n\n"
        f"{cost_table}"
        f"{all_rooms_block}\n\n"
        f"---\n"
        f"{customize_prompt}"
    )


def _get_all_dest_rooms(dest_id: int) -> List[Dict]:
    """Return all active rooms for a destination (SQLite + PostgreSQL)."""
    try:
        from database import _USE_PG, _sqlite_conn, _pg_conn
        sql_sqlite = """
            SELECT rm.id, rm.resort_id, rm.name, rm.view_type, rm.suitable_for,
                   rm.budget_level, rm.price_per_night, rm.breakfast_included,
                   rm.source_url, rm.highlights,
                   rs.name AS resort_name, rs.address
            FROM vp_room rm
            JOIN vp_resort rs ON rm.resort_id = rs.id
            WHERE rs.destination_id = ? AND rm.is_active = 1 AND rs.is_active = 1
            ORDER BY rm.price_per_night ASC"""
        sql_pg = sql_sqlite.replace("= ?", "= %s")
        if _USE_PG:
            import psycopg2.extras
            conn = _pg_conn()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql_pg, (dest_id,))
            rows = [dict(r) for r in cur.fetchall()]
            cur.close(); conn.close()
        else:
            conn = _sqlite_conn()
            rows = [dict(r) for r in conn.execute(sql_sqlite, (dest_id,)).fetchall()]
            conn.close()
        return rows
    except Exception as e:
        print(f"[DB] _get_all_dest_rooms error: {e}")
        return []


def _handle_vp_planning(user_message: str, history: List[Dict]) -> Optional[str]:
    msg_norm = _normalize(user_message)
    state = _get_vp_state(history)

    # ── Đặt lịch sau khi đã có lịch trình ─────────────────────────────────────
    if state == "waiting_vp_contact":
        ctx = _extract_vp_booking_context(history)
        info = _parse_vp_contact_info(user_message)
        missing = _vp_contact_missing(info)
        if missing:
            return (
                f"⚠️ Còn thiếu: **{', '.join(missing)}**.\n\n"
                f"{_format_vp_contact_form(ctx)}"
            )
        adults, children = _vp_party_size(ctx.get("who", "couple"))
        num_guests = info.get("num_guests") or adults + children
        notes_parts = [
            f"Vinpearl | {_who_label(ctx.get('who', 'couple'))}",
            f"Ngân sách: {_budget_label_vp(ctx.get('budget', 'trung'))}",
            f"{ctx.get('days', 2)} ngày",
        ]
        if info.get("notes"):
            notes_parts.append(info["notes"])
        booking_data = {
            "city": ctx.get("dest_name", ""),
            "hotel_name": ctx.get("resort", "Vinpearl"),
            "room_type": ctx.get("room_type", "Chưa xác định"),
            "guest_name": info["guest_name"],
            "phone": info["phone"],
            "email": info["email"],
            "checkin": info.get("checkin", ""),
            "checkout": info.get("checkout", ""),
            "num_guests": num_guests,
            "notes": " | ".join(notes_parts),
        }
        booking_id, telegram_ok = _save_booking_and_notify(booking_data)
        id_label = f"`#{booking_id:04d}`" if booking_id else "`#---`"
        tg_line = (
            "📲 Đã gửi thông báo tới nhóm CSKH trên Telegram.\n"
            if telegram_ok
            else "ℹ️ *(Chưa gửi Telegram — cấu hình TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID trong .env)*\n"
        )
        return (
            f"{_VP_MARKER_BOOKING_DONE} đã được ghi nhận!**\n\n"
            f"📌 **Mã yêu cầu:** {id_label}\n\n"
            f"- 👤 **Họ tên:** {booking_data['guest_name']}\n"
            f"- 📞 **SĐT:** {booking_data['phone']}\n"
            f"- ✉️ **Email:** {booking_data['email']}\n"
            f"- 🏨 **Phòng:** {booking_data['room_type']} — {booking_data['hotel_name']}\n"
            f"- 📍 **Điểm đến:** {booking_data['city']}\n"
            + (f"- 📅 Check-in: {booking_data['checkin']}\n" if booking_data["checkin"] else "")
            + (f"- 📅 Check-out: {booking_data['checkout']}\n" if booking_data["checkout"] else "")
            + f"- 👥 Số khách: {booking_data['num_guests']}\n\n"
            f"{tg_line}\n"
            "💡 *Nhân viên CSKH Vinpearl sẽ liên hệ trong vòng **24 giờ** để xác nhận lịch và thanh toán.*"
        )

    # Correction: restart the flow (preserve days from history)
    if state is not None and any(k in msg_norm for k in ["làm lại", "lam lai", "bắt đầu lại", "bat dau lai", "reset"]):
        days = _extract_trip_days(history)
        days_note = f"\n*(Chuyến đi: **{days} ngày** Phú Quốc)*" if days != 2 else ""
        return (
            f"🤝 **Câu 1/3 — Bạn đi với ai?**{days_note}\n\n"
            "1. 👫 Cặp đôi\n"
            "2. 👨‍👩‍👧 Gia đình (có con nhỏ)\n"
            "3. 👥 Nhóm bạn\n"
            "4. 🧍 Một mình\n\n"
            "*(Gõ số hoặc mô tả)*"
        )

    # ── Customize state — xử lý mọi yêu cầu tùy chỉnh ──────────────────────────
    if state in ("result_shown", "waiting_customize"):
        if _is_vp_booking_intent(msg_norm, history):
            return _format_vp_contact_form(_extract_vp_booking_context(history))

        days = _extract_trip_days(history)
        dest_id, dest_name = _extract_dest_from_history(history)
        who = _extract_who_from_history(history)
        budget = _extract_budget_from_history_vp(history)
        all_rooms = _get_all_dest_rooms(dest_id)

        # Quick shortcut: menu items 3/4
        if msg_norm.strip() == "3" or any(k in msg_norm for k in ["thích biển", "biển hơn", "nghỉ dưỡng hơn"]):
            room = _find_vp_room(who, budget, "biển", dest_id)
            deal = _find_vp_deal(room, dest_id)
            return _build_vp_timeline(who, "biển", room, deal, days, dest_name, dest_id, all_rooms, budget)

        if msg_norm.strip() == "4" or any(k in msg_norm for k in ["vui chơi hơn", "vinwonders hơn", "thêm vinwonders"]):
            room = _find_vp_room(who, budget, "vui chơi", dest_id)
            deal = _find_vp_deal(room, dest_id)
            return _build_vp_timeline(who, "vui chơi", room, deal, days, dest_name, dest_id, all_rooms, budget)

        # Option 6 / "giữ nguyên" / "ok" → đặt lịch
        if msg_norm.strip() == "6" or any(k in msg_norm for k in ["giữ nguyên", "giu nguyen", "không đổi",
                                                                    "ok", "được rồi", "duoc roi", "ổn rồi"]):
            return _format_vp_contact_form(_extract_vp_booking_context(history))

        # Option 1 / room-switch by index or name
        room_switched = _try_switch_room(msg_norm, all_rooms, who, budget, nights=days - 1 if days > 1 else 1)
        if room_switched:
            # Try to get the current style from history
            cur_style = "cả hai"
            for m in reversed(history):
                if m["role"] == "assistant" and _VP_MARKER_RESULT in m["content"]:
                    c = m["content"]
                    if "biển & nghỉ dưỡng" in c.lower() or ("biển" in c[:500] and "vinwonders" not in c[:500].lower()):
                        cur_style = "biển"
                    elif "vui chơi" in c[:500].lower():
                        cur_style = "vui chơi"
                    break
            deal = _find_vp_deal(room_switched, dest_id)
            return _build_vp_timeline(who, cur_style, room_switched, deal, days, dest_name, dest_id, all_rooms, budget)

        # Option 2 / day-change
        new_days = _try_extract_day_change(msg_norm, days)
        if new_days and new_days != days:
            cur_style = "cả hai"
            cur_room_data = None
            for m in reversed(history):
                if m["role"] == "assistant" and _VP_MARKER_RESULT in m["content"]:
                    c = m["content"]
                    if "biển & nghỉ dưỡng" in c.lower():
                        cur_style = "biển"
                    elif "vui chơi" in c[:500].lower():
                        cur_style = "vui chơi"
                    break
            room = _find_vp_room(who, budget, cur_style, dest_id)
            deal = _find_vp_deal(room, dest_id)
            return _build_vp_timeline(who, cur_style, room, deal, new_days, dest_name, dest_id, all_rooms, budget)

        # Option 5 / activity change request — detect by day/slot keywords
        if any(k in msg_norm for k in ["đổi hoạt động", "thay hoạt động", "ngày ", "buổi ",
                                        "doi hoat dong", "thay hoat dong",
                                        "ngay ", "buoi ", "doi ngay", "them hoat"]):
            return _handle_activity_change_request(msg_norm, history, who, budget, days, dest_id, dest_name, all_rooms)

        # Option 1 prompt / menu shown / user typed "1" or "2"
        if msg_norm.strip() == "1":
            return (
                f"{_MARKER_VP_CUSTOMIZE} — đổi phòng?**\n\n"
                f"Gõ **số thứ tự** hoặc **tên phòng** từ bảng so sánh phía trên.\n"
                f"*(Ví dụ: 'đổi sang phòng 3' hoặc 'Family Deluxe')*"
            )
        if msg_norm.strip() == "2":
            return (
                f"{_MARKER_VP_CUSTOMIZE} — số ngày?**\n\n"
                f"Hiện tại: **{days} ngày**. Bạn muốn thay đổi thế nào?\n"
                "*(Gõ ví dụ: 'thêm 1 ngày', 'rút còn 3 ngày', hoặc số ngày cụ thể như '7 ngày')*"
            )
        if msg_norm.strip() == "5":
            return (
                f"{_MARKER_VP_CUSTOMIZE} — đổi hoạt động?**\n\n"
                "Cho tôi biết bạn muốn thay gì, ví dụ:\n"
                "- *'ngày 2 buổi chiều đổi sang thăm Tháp Bà Ponagar'*\n"
                "- *'thêm hoạt động kayak ngày 3'*\n"
                "- *'bỏ tour lặn, thay bằng spa'*\n\n"
                "*(Mô tả tự do — tôi sẽ cập nhật lịch trình)*"
            )

        # For result_shown: forward to customize prompt; for waiting_customize: stay silent → AI
        if state == "result_shown":
            return _build_customize_prompt()
        return None

    # ── Promotion / deal query — no planning needed ────────────────────────
    _promo_kws = [
        "ưu đãi", "uu dai", "khuyến mãi", "khuyen mai", "giảm giá", "giam gia",
        "deal", "promotion", "offer", "promo", "sale", "ưu đai",
    ]
    if any(k in msg_norm for k in _promo_kws) and state is None:
        dest_id, dest_name = _detect_vp_dest(msg_norm)
        # Pull all deals for destination (resort_id=0 → match dest-level deals)
        from database import get_vp_promotions
        db_deals = get_vp_promotions(dest_id, 0)
        # Also check static VINPEARL_DEALS as fallback
        static_deals = [d for d in VINPEARL_DEALS]

        rows = []
        if db_deals:
            for d in db_deals:
                disc = d.get("discount_value") or ""
                disc_str = f"{int(disc)}%" if disc else "Xem chi tiết"
                rows.append(
                    f"| **{d.get('name','')}** | {disc_str} | "
                    f"{d.get('condition_text','') or d.get('note','')} | "
                    f"[Xem]({d.get('source_url','https://vinpearl.com/vi/khuyen-mai')}) |"
                )
        else:
            for d in static_deals:
                rows.append(
                    f"| **{d['title']}** | {d['discount']} | "
                    f"{d['condition']} | "
                    f"[Xem]({d['source_url']}) |"
                )

        table = (
            f"### 🎁 Ưu đãi Vinpearl {dest_name} đang áp dụng\n\n"
            "| Ưu đãi | Giảm | Điều kiện | Chi tiết |\n"
            "|---|:---:|---|:---:|\n"
            + "\n".join(rows)
        )
        table += (
            "\n\n> 💡 Ưu đãi có thể thay đổi theo thời điểm. "
            "Kiểm tra chính xác tại [vinpearl.com/vi/khuyen-mai](https://vinpearl.com/vi/khuyen-mai).\n\n"
            f"Bạn muốn **lên lịch trình** ghé thăm Vinpearl {dest_name} không? "
            f"Chỉ cần nói ví dụ: *\"Lên lịch 3 ngày {dest_name}\"*"
        )
        return table

    # Initial trigger
    if state is None:
        if _is_vp_planning_intent(msg_norm):
            dest_id, dest_name = _detect_vp_dest(msg_norm)
            days = _extract_days(user_message) or 2
            days = max(1, min(days, 14))

            # Try to detect info already provided in this first message
            pre_who = _extract_who(msg_norm)
            # _extract_who returns "couple" as default even when not mentioned
            # Only trust it if there's an explicit who keyword
            _who_explicit_kws = [
                "gia đình", "gia dinh", "con ", "trẻ em", "ba mẹ", "bố mẹ",
                "nhóm", "nhom", "bạn bè", "ban be", "hội",
                "cặp đôi", "cap doi", "vợ chồng", "bạn trai", "bạn gái", "người yêu",
                "một mình", "mot minh", "1 mình", "di minh", "mình đi", "solo",
                " 1 người", " 2 người", " 3 người", " 4 người",
            ]
            who_known = any(k in msg_norm for k in _who_explicit_kws)
            pre_who = pre_who if who_known else None

            pre_budget = _extract_budget_vp(msg_norm, days)
            budget_known = pre_budget != "mơ hồ"

            pre_style_raw = _extract_vp_style(msg_norm)
            _style_explicit_kws = [
                "biển", "bien", "beach", "tắm", "bơi", "nghỉ dưỡng", "nghi duong",
                "vui chơi", "vui choi", "vinwonders", "safari", "giải trí",
                "cả hai", "ca hai",
            ]
            style_known = any(k in msg_norm for k in _style_explicit_kws)
            pre_style = pre_style_raw if style_known else None

            trip_note = f"\n*(Chuyến đi: **{days} ngày** tại **{dest_name}** — Vinpearl)*"
            if days == 2 and dest_name == "Phú Quốc":
                trip_note = ""

            # --- Fast-track: all 3 known → generate result directly ---
            # --- Fast-track: who + budget known → generate directly (default style = "cả hai") ---
            if who_known and budget_known:
                resolved_style = pre_style if style_known else "cả hai"
                room = _find_vp_room(pre_who, pre_budget, resolved_style, dest_id)
                deal = _find_vp_deal(room, dest_id)
                all_rooms = _get_all_dest_rooms(dest_id)
                return _build_vp_timeline(pre_who, resolved_style, room, deal, days, dest_name, dest_id, all_rooms, pre_budget)

            # --- who known, skip Q1 → ask Q2 ---
            if who_known:
                who_embed = f" 👤*(đi với: {_who_label(pre_who)})*"
                return (
                    f"💰 **Câu 2/3 — Ngân sách** mỗi đêm tại **{dest_name}** khoảng bao nhiêu?{trip_note}{who_embed}\n\n"
                    "1. 💚 Thấp — dưới 3 triệu/đêm\n"
                    "2. 💛 Trung bình — 3–6 triệu/đêm\n"
                    "3. 🔴 Cao — trên 6 triệu/đêm\n\n"
                    "*(Gõ số hoặc mô tả)*"
                )

            # --- budget known, need Q1 + Q3 (skip Q2) ---
            budget_note_line = ""
            if budget_known:
                budget_note_line = f"\n💰*(ngân sách: {pre_budget})* ← đã ghi nhận, sẽ bỏ qua câu hỏi ngân sách"

            return (
                f"🤝 **Câu 1/3 — Bạn đi với ai?**{trip_note}{budget_note_line}\n\n"
                "1. 👫 Cặp đôi\n"
                "2. 👨‍👩‍👧 Gia đình (có con nhỏ)\n"
                "3. 👥 Nhóm bạn\n"
                "4. 🧍 Một mình\n\n"
                "*(Gõ số hoặc mô tả)*"
            )
        return None

    # Q1 answered → ask Q2 (or skip if budget already embedded in Q1 message)
    if state == "waiting_q1":
        who = _extract_who(msg_norm)
        dest_id, dest_name = _extract_dest_from_history(history)

        # Check if budget was already embedded in Q1 bot message
        budget_pre = None
        for m_hist in history:
            if m_hist["role"] == "assistant" and _VP_MARKER_Q1 in m_hist["content"]:
                bm = re.search(r"💰\*\(ngân sách:\s*([^)]+)\)", m_hist["content"])
                if bm:
                    budget_pre = bm.group(1).strip()
                break

        if budget_pre and budget_pre in ("thấp", "trung", "cao"):
            # Skip Q2 — go straight to Q3
            return (
                f"🏖️ **Câu 2/2 — Phong cách** chuyến đi?\n"
                f"*(Đi với: {_who_label(who)} · Ngân sách: {_budget_label_vp(budget_pre)})*\n\n"
                "1. 🌊 **Biển & nghỉ dưỡng** — tắm biển, bể bơi, spa\n"
                "2. 🎢 **Vui chơi giải trí** — VinWonders, Safari\n"
                "3. 🌟 **Cả hai** — nửa biển, nửa vui chơi\n\n"
                "*(Gõ số hoặc mô tả)*"
            )

        return (
            f"💰 **Câu 2/3 — Ngân sách** mỗi đêm tại **{dest_name}** khoảng bao nhiêu?\n"
            f"*(Đi với: {_who_label(who)})*\n\n"
            "1. 💚 Thấp — dưới 3 triệu/đêm\n"
            "2. 💛 Trung bình — 3–6 triệu/đêm\n"
            "3. 🔴 Cao — trên 6 triệu/đêm\n\n"
            "*(Gõ số hoặc mô tả)*"
        )

    def _generate_from_history(user_msg_norm: str) -> str:
        who = _extract_who_from_history(history)
        budget = _extract_budget_from_history_vp(history)
        style_raw = _extract_vp_style(user_msg_norm)
        _style_kws = ["biển", "bien", "beach", "tắm", "bơi", "nghỉ dưỡng",
                      "vui chơi", "vui choi", "vinwonders", "safari", "cả hai", "ca hai"]
        style = style_raw if any(k in user_msg_norm for k in _style_kws) else "cả hai"
        days = _extract_trip_days(history, user_message)
        dest_id, dest_name = _extract_dest_from_history(history)
        room = _find_vp_room(who, budget, style, dest_id)
        deal = _find_vp_deal(room, dest_id)
        all_rooms = _get_all_dest_rooms(dest_id)
        return _build_vp_timeline(who, style, room, deal, days, dest_name, dest_id, all_rooms, budget)

    # Q2 answered → clarify if vague, else generate directly (no need for Q3)
    if state == "waiting_q2":
        days_q2 = _extract_trip_days(history, user_message)
        budget = _extract_budget_vp(msg_norm, days_q2)
        if budget == "mơ hồ":
            return (
                "💡 **Làm rõ ngân sách** — Bạn đang nghĩ tới tầm nào?\n\n"
                "- **Dưới 3 tr/đêm**: Vinpearl Discovery / Standard — giá tốt nhất\n"
                "- **3–6 tr/đêm**: Vinpearl Resort Deluxe — view biển đẹp, bể bơi vô cực\n"
                "- **Trên 6 tr/đêm**: Suite hoặc Pool Villa — sang trọng nhất Vinpearl\n\n"
                "Bạn nghĩ tầm nào phù hợp hơn?"
            )
        return _generate_from_history(msg_norm)

    # After clarify → generate directly
    if state == "waiting_clarify":
        return _generate_from_history(msg_norm)

    # Q3 answered → generate full timeline (kept for back-compat with old sessions)
    if state == "waiting_q3":
        return _generate_from_history(msg_norm)

    return None


_VP_REDIRECT_MSG = (
    "🌴 **VinBot** chỉ hỗ trợ lập lịch trình tại các điểm đến **Vinpearl**.\n\n"
    "Hiện tại tôi có thể giúp bạn tại:\n\n"
    "| Điểm đến | Nổi bật |\n"
    "|---|---|\n"
    "| 🏝️ **Phú Quốc** | Đảo ngọc, VinWonders, Safari, resort sang |\n"
    "| 🌊 **Nha Trang** | Biển đẹp, VinWonders, hải sản tươi |\n"
    "| 🏖️ **Nam Hội An** | Vui chơi ven biển, cách phố cổ 30 phút |\n"
    "| 🌅 **Cửa Hội – Nghệ An** | Biển yên tĩnh, gần thành phố Vinh |\n"
    "| ⚓ **Hải Phòng** | Đảo Cát Bà, cảng biển, ẩm thực phong phú |\n\n"
    "Bạn muốn lên lịch trình tại điểm nào? Chỉ cần nói ví dụ:\n"
    "*\"Lên lịch 3 ngày Nha Trang\"* hoặc *\"2N1Đ Phú Quốc\"*"
)


def _rule_based_reply(user_message: str, history: List[Dict[str, str]] | None = None) -> str | None:
    history = history or []
    msg = _normalize(user_message)

    # 0a. Vinpearl planning flow (highest priority)
    vp_reply = _handle_vp_planning(user_message, history)
    if vp_reply:
        return vp_reply

    # 0. Booking flow (bỏ qua nếu đang trong luồng Vinpearl — VP xử lý đặt lịch riêng)
    if not _had_vp_itinerary(history) or not _is_vp_booking_intent(msg, history):
        booking_reply = _handle_booking(user_message, history)
        if booking_reply:
            return booking_reply

    # 1–7. Any travel-related query → redirect to Vinpearl destinations
    _travel_kws = [
        "đi ", "muốn đi", "du lịch", "lịch trình", "lich trinh", "travel", "trip",
        "tour", "khách sạn", "hotel", "gợi ý", "đề xuất", "recommend", "nên đi",
        "điểm đến", "resort", "nghỉ dưỡng", "nghi duong",
    ]
    if any(k in msg for k in _travel_kws):
        return _VP_REDIRECT_MSG

    return None



# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def get_travel_response(history: List[Dict[str, str]], session_id: str = "") -> str:
    """Public API — returns only the reply string (backward-compatible)."""
    reply, _ = await get_travel_response_with_meta(history, session_id=session_id)
    return reply


async def get_travel_response_with_meta(
    history: List[Dict[str, str]],
    session_id: str = "",
) -> tuple:
    """
    Returns (reply: str, meta: dict) where meta contains token counts,
    cost, provider, model. Also persists a row to chat_logs.

    Priority order:
      1. _rule_based_reply  → Vinpearl Q&A flow, booking, city guides (chatbot.py)
      2. vinpearl_bot       → deals, room listing, scope-guard (vinpearl_bot.py)
      3. AI provider        → free-form questions
    """
    last_user_msg = next(
        (m["content"] for m in reversed(history) if m["role"] == "user"), ""
    )

    # ── 1. Rule-based (Vinpearl planning Q&A, booking, etc.) ─────────────────
    rule_reply = _rule_based_reply(last_user_msg, history)
    if rule_reply:
        meta = _build_rule_meta(history, rule_reply)
        _persist_chat_log(history, rule_reply, meta, session_id)
        return rule_reply, meta

    # ── 2. vinpearl_bot (deals list, room list, scope/redirect) ──────────────
    from services.vinpearl_bot import respond as vinpearl_respond
    try:
        vb_reply = await vinpearl_respond(history)
        if vb_reply:
            meta = _build_rule_meta(history, vb_reply)
            _persist_chat_log(history, vb_reply, meta, session_id)
            return vb_reply, meta
    except Exception as e:
        print(f"[vinpearl_bot] error: {e}")

    # ── 3. AI provider ────────────────────────────────────────────────────────
    return await _legacy_response(history, session_id=session_id)


async def _legacy_response(history: List[Dict[str, str]], session_id: str = "") -> tuple:
    """AI provider fallback — called only when both rule-based and vinpearl_bot return nothing."""
    provider = detect_provider()
    print(f"[AI] Using provider: {provider}")

    # ── AI provider ────────────────────────────────────────────────────────────
    try:
        reply, usage = None, {}
        if provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            reply, usage = await _call_openai_compat(
                history, api_key=os.getenv("OPENAI_API_KEY", ""), model=model,
            )
        elif provider == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            reply, usage = await _call_gemini(
                history, api_key=os.getenv("GEMINI_API_KEY", ""), model=model,
            )
        elif provider == "claude":
            model = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
            reply, usage = await _call_claude(
                history, api_key=os.getenv("CLAUDE_API_KEY", ""), model=model,
            )
        elif provider == "openrouter":
            model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            reply, usage = await _call_openai_compat(
                history,
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                model=model,
                base_url="https://openrouter.ai/api/v1",
            )
        elif provider == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama3")
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1"
            reply, usage = await _call_openai_compat(
                history, api_key="ollama", model=model, base_url=base_url,
            )

        if reply:
            meta = {"provider": provider, "model": model, **usage}
            _persist_chat_log(history, reply, meta, session_id)
            return reply, meta

    except Exception as e:
        print(f"[{provider}] error: {e}")

    # ── Final fallback ─────────────────────────────────────────────────────────
    city = _extract_city_from_history(history)
    if city:
        reply = (
            f"Bạn muốn tôi tư vấn thêm về **{city.title()}** không? 😊\n\n"
            "Tôi có thể giúp về: **khách sạn**, **ẩm thực**, **lịch trình**, **phương tiện di chuyển**."
        )
    else:
        reply = (
            "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. 😊\n\n"
            "Tôi có thể tư vấn về:\n"
            "🇻🇳 **Việt Nam:** Hà Nội, Đà Nẵng, Hội An, Sapa, Phú Quốc\n"
            "🌏 **Châu Á:** Bangkok, Tokyo, Bali, Singapore\n"
            "🌍 **Châu Âu:** Paris, Rome, Barcelona\n\n"
            "Bạn muốn khám phá điểm đến nào?"
        )
    meta = _build_rule_meta(history, reply)
    _persist_chat_log(history, reply, meta, session_id)
    return reply, meta


def _build_rule_meta(history: List[Dict], reply: str) -> Dict:
    """Build meta dict for rule-based (no real token counts — use estimates)."""
    all_input = " ".join(m["content"] for m in history)
    input_t  = _estimate_tokens(all_input)
    output_t = _estimate_tokens(reply)
    return {
        "provider":      "rule-based",
        "model":         "",
        "input_tokens":  input_t,
        "output_tokens": output_t,
        "total_tokens":  input_t + output_t,
        "cost_usd":      0.0,
    }


def _persist_chat_log(history: List[Dict], reply: str, meta: Dict, session_id: str) -> None:
    """Write one row to chat_logs, silently ignoring DB errors."""
    try:
        from database import log_chat
        last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
        log_chat({
            "session_id":    session_id,
            "provider":      meta.get("provider", "rule-based"),
            "model":         meta.get("model", ""),
            "user_message":  last_user,
            "bot_reply":     reply,
            "input_tokens":  meta.get("input_tokens", 0),
            "output_tokens": meta.get("output_tokens", 0),
            "total_tokens":  meta.get("total_tokens", 0),
            "cost_usd":      meta.get("cost_usd", 0.0),
        })
    except Exception as e:
        print(f"[chat_log] persist error (non-fatal): {e}")

