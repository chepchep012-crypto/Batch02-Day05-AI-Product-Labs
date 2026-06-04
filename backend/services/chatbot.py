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

SYSTEM_PROMPT = """You are TravelBot, an expert AI travel assistant for the 
Day5-6 Hackathon Travel application. You help users plan trips, recommend 
destinations, suggest hotels, restaurants, activities, and provide travel tips.
Always respond in the same language the user writes in (Vietnamese or English).
Keep answers friendly, concise and helpful."""

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
# Provider implementations
# ---------------------------------------------------------------------------

async def _call_openai_compat(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    base_url: str | None = None,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """OpenAI / OpenRouter / Ollama — all share the same OpenAI-compatible API."""
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
    return response.choices[0].message.content.strip()


async def _call_gemini(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """Google Gemini via google-generativeai SDK."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    # Convert history → Gemini format (all except last message)
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
    return response.text.strip()


async def _call_claude(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """Anthropic Claude via anthropic SDK."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    response = await client.messages.create(
        model=model,
        system=system_prompt,
        messages=messages,
        max_tokens=800,
    )
    return response.content[0].text.strip()


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
        "Vui lòng điền và gửi lại:\n\n"
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

        # Save to DB
        try:
            from database import create_booking
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
            booking_id = create_booking(booking_data)
            id_label = f"`#{booking_id:04d}`"
        except Exception as e:
            print(f"[DB] create_booking error: {e}")
            booking_data = {
                "hotel_name": hotel.get("name", "").split("⭐")[0].strip(),
                "room_type": ROOM_TYPE_MAP.get(room_key, room_key or "Không xác định"),
                "guest_name": info.get("guest_name", ""),
                "phone": info.get("phone", ""),
                "email": info.get("email", ""),
                "checkin": info.get("checkin", ""),
                "checkout": info.get("checkout", ""),
                "num_guests": info.get("num_guests", 1),
            }
            id_label = "`#---`"

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
            f"- 👤 Họ tên: {booking_data['guest_name'] or '*(chưa cung cấp)*'}\n"
            f"- 📞 SĐT: {booking_data['phone'] or '*(chưa cung cấp)*'}\n"
            f"- 📅 Check-in: {booking_data['checkin'] or '*(chưa xác định)*'}\n"
            f"- 📅 Check-out: {booking_data['checkout'] or '*(chưa xác định)*'}\n"
            f"- 👥 Số khách: {booking_data['num_guests']}\n\n"
            f"**📬 Liên hệ khách sạn để xác nhận:**\n"
            f"- 📞 {hotel_phone}\n"
            f"- ✉️ {hotel_email}\n"
            + (f"- 🌐 [{hotel_web.replace('https://','').split('/')[0]}]({hotel_web})\n" if hotel_web else "")
            + f"\n💡 *Trạng thái: **Chờ xác nhận** — Khách sạn sẽ liên hệ trong vòng 24h.*"
        )

    return None


def _rule_based_reply(user_message: str, history: List[Dict[str, str]] | None = None) -> str | None:
    history = history or []
    msg = _normalize(user_message)

    # 0. Booking flow takes priority
    booking_reply = _handle_booking(user_message, history)
    if booking_reply:
        return booking_reply

    # 1. Detect city trong tin nhắn hiện tại
    current_city: str | None = None
    for kw, city in KEYWORD_MAP.items():
        if kw in msg:
            current_city = city
            break

    # 2. Detect topic trong tin nhắn hiện tại
    current_topic: str | None = None
    for kw, topic in TOPIC_MAP.items():
        if kw in msg:
            current_topic = topic
            break

    # 3. Nếu hỏi khách sạn/hotel
    if current_topic == "hotel":
        city = current_city or _extract_city_from_history(history)
        if city and city in CITY_HOTEL_INFO:
            return CITY_HOTEL_INFO[city]
        return (
            "Bạn muốn tìm khách sạn ở **thành phố nào**? 🏨\n\n"
            "Tôi có thông tin về: Hà Nội, Đà Nẵng, Hội An, Sapa, Phú Quốc, Bangkok, Tokyo, Paris."
        )

    # 4. Nếu hỏi về lịch trình
    if current_topic == "itinerary":
        city = current_city or _extract_city_from_history(history)
        days = _extract_days(user_message) or _extract_days_from_history(history)
        style = _extract_style(user_message) or _extract_style_from_history(history)

        if city and days:
            return _build_itinerary(city, days, style)

        if city and not days:
            return (
                f"Bạn muốn đi **{city.title()}** bao nhiêu ngày? 🗺️\n\n"
                "Và phong cách du lịch của bạn là gì?\n"
                "- 🏖️ **Nghỉ dưỡng** — resort, spa, biển\n"
                "- 🧭 **Khám phá** — tham quan, trekking\n"
                "- 🍜 **Ẩm thực** — foodie tour\n"
                "- 🎭 **Văn hoá** — di tích, lịch sử"
            )

        return (
            "Bạn muốn lên lịch trình ở **thành phố nào** và **bao nhiêu ngày**? 🗺️\n\n"
            "Ví dụ: *'lịch trình 7 ngày Đà Nẵng nghỉ dưỡng'*"
        )

    # 5. Nếu có city trong tin nhắn hiện tại → trả info city
    if current_city and current_city in FALLBACK_RESPONSES:
        return FALLBACK_RESPONSES[current_city]

    # 6. Gợi ý điểm đến (inspire)
    inspire_kws = ["gợi ý", "goi y", "đề xuất", "de xuat", "inspire", "recommend",
                   "điểm đến", "muốn đi", "nên đi", "thú vị", "hay ho"]
    if any(k in msg for k in inspire_kws):
        return CITY_INSPIRE["mặc định"]

    # 7. Generic travel keyword
    if any(w in msg for w in ["du lịch", "travel", "trip", "tour", "khách sạn", "hotel"]):
        city = _extract_city_from_history(history)
        if city:
            return (
                f"Bạn muốn tôi tư vấn thêm về **{city.title()}** không?\n\n"
                "Tôi có thể giúp: lịch trình, khách sạn, ẩm thực, phương tiện di chuyển."
            )
        return (
            "Tôi có thể giúp bạn khám phá các điểm đến tuyệt vời! 🌏\n\n"
            "Hãy cho tôi biết:\n"
            "1. Bạn muốn đi **đâu**?\n"
            "2. Thời gian **bao lâu**?\n"
            "3. Ngân sách **khoảng bao nhiêu**?\n\n"
            "Tôi sẽ gợi ý lịch trình phù hợp nhất cho bạn!"
        )

    return None



# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

async def get_travel_response(history: List[Dict[str, str]]) -> str:
    # Vinpearl bot xử lý toàn bộ: phân loại câu hỏi, 3 chức năng, grounding LLM,
    # điều hướng (ngoài Vinpearl / ngoài chủ đề). Dữ liệu & luật ở data/vinpearl.json.
    from services.vinpearl_bot import respond as vinpearl_respond
    try:
        return await vinpearl_respond(history)
    except Exception as e:
        print(f"[vinpearl] fatal: {e} — fallback legacy")

    return await _legacy_response(history)


async def _legacy_response(history: List[Dict[str, str]]) -> str:
    provider = detect_provider()
    print(f"[AI] Using provider: {provider}")

    try:
        if provider == "openai":
            return await _call_openai_compat(
                history,
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            )

        elif provider == "gemini":
            return await _call_gemini(
                history,
                api_key=os.getenv("GEMINI_API_KEY", ""),
                model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            )

        elif provider == "claude":
            return await _call_claude(
                history,
                api_key=os.getenv("CLAUDE_API_KEY", ""),
                model=os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307"),
            )

        elif provider == "openrouter":
            return await _call_openai_compat(
                history,
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo"),
                base_url="https://openrouter.ai/api/v1",
            )

        elif provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1"
            return await _call_openai_compat(
                history,
                api_key="ollama",  # Ollama không cần key thật
                model=os.getenv("OLLAMA_MODEL", "llama3"),
                base_url=base_url,
            )

    except Exception as e:
        print(f"[{provider}] error: {e}")

    # Fallback: rule-based với context awareness
    last_user_msg = next(
        (m["content"] for m in reversed(history) if m["role"] == "user"), ""
    )
    reply = _rule_based_reply(last_user_msg, history)
    if reply:
        return reply

    # Kiểm tra có city nào trong history không để trả lời contextual
    city = _extract_city_from_history(history)
    if city:
        return (
            f"Bạn muốn tôi tư vấn thêm về **{city.title()}** không? 😊\n\n"
            "Tôi có thể giúp về: **khách sạn**, **ẩm thực**, **lịch trình**, **phương tiện di chuyển**."
        )

    return (
        "Xin lỗi, tôi chưa hiểu câu hỏi của bạn. 😊\n\n"
        "Tôi có thể tư vấn về:\n"
        "🇻🇳 **Việt Nam:** Hà Nội, Đà Nẵng, Hội An, Sapa, Phú Quốc\n"
        "🌏 **Châu Á:** Bangkok, Tokyo, Bali, Singapore\n"
        "🌍 **Châu Âu:** Paris, Rome, Barcelona\n\n"
        "Bạn muốn khám phá điểm đến nào?"
    )

