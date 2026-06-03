import os
from typing import List, Dict

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
    "hà nội": "Hà Nội là thủ đô ngàn năm văn hiến của Việt Nam! 🏛️\n\n**Điểm tham quan nổi bật:**\n- Hồ Hoàn Kiếm & Tháp Rùa\n- Văn Miếu Quốc Tử Giám\n- Phố cổ 36 phố phường\n- Lăng Bác Hồ\n\n**Ẩm thực phải thử:**\n- Phở Bát Đàn\n- Bún chả Hương Liên\n- Chả cá Lã Vọng\n\nBạn dự định đi mấy ngày?",
    "đà nẵng": "Đà Nẵng – thành phố đáng sống! 🌊\n\n**Điểm nổi bật:**\n- Bãi biển Mỹ Khê (top 6 bãi biển đẹp thế giới)\n- Cầu Rồng phun lửa (cuối tuần)\n- Bà Nà Hills & Cầu Vàng\n- Phố cổ Hội An (30 phút)\n\n**Thời điểm tốt nhất:** Tháng 1–8\n\nBạn muốn biết thêm về khách sạn hay hoạt động?",
    "hội an": "Hội An – Phố cổ huyền diệu! 🏮\n\n**Không thể bỏ qua:**\n- Phố đèn lồng Hội An\n- Chùa Cầu Nhật Bản\n- Làng rau Trà Quế\n- Lăng Mộ & Nhà cổ\n\n**Ẩm thực đặc sắc:**\n- Cao lầu\n- Mì Quảng\n- Bánh mì Phượng\n\nThích chụp ảnh? Đến lễ hội đèn lồng vào 14 âm lịch nhé!",
    "sapa": "Sa Pa – Vùng cao mây phủ! 🏔️\n\n**Trải nghiệm:**\n- Trekking Fansipan (3143m – Nóc nhà Đông Dương)\n- Ruộng bậc thang Mù Cang Chải (tháng 9-10)\n- Bản làng người H'Mông, Dao Đỏ\n- Chợ phiên Bắc Hà\n\n**Lưu ý:** Mang áo ấm, nhiệt độ có thể 5°C vào mùa đông.\n\nBạn muốn đặt tour trekking không?",
    "phú quốc": "Phú Quốc – Đảo Ngọc Việt Nam! 🌴\n\n**Điểm đến:**\n- Bãi Sao, Bãi Dài, Bãi Trường\n- VinWonders & Safari\n- Chợ đêm Dinh Cậu\n- Làng chài Hàm Ninh\n\n**Đặc sản:** Nước mắm Phú Quốc, Nhum biển, Ghẹ hấp\n\n**Bay từ HCM:** ~1 giờ | Từ HN: ~2 giờ\n\nMùa đẹp nhất: Tháng 11 – tháng 4.",
    "bangkok": "Bangkok – City of Angels! 🛕\n\n**Must-see:**\n- Grand Palace & Wat Phra Kaew\n- Wat Arun (Temple of Dawn)\n- Chatuchak Weekend Market\n- Khao San Road\n- Floating Markets\n\n**Food:** Pad Thai, Tom Yum, Mango Sticky Rice\n\n**Getting around:** BTS Skytrain, MRT, Grab\n\nHow many days are you planning?",
    "paris": "Paris – The City of Light! 🗼\n\n**Must-see:**\n- Eiffel Tower\n- Louvre Museum\n- Notre-Dame Cathedral\n- Montmartre & Sacré-Cœur\n- Seine River Cruise\n\n**Food:** Croissants, Crêpes, French onion soup\n\n**Best time:** April–June, Sept–Oct\n\nWould you like hotel or restaurant recommendations?",
    "tokyo": "Tokyo – Where tradition meets future! 🗾\n\n**Top spots:**\n- Shibuya Crossing\n- Senso-ji Temple (Asakusa)\n- Shinjuku & Harajuku\n- teamLab Borderless\n- Mount Fuji day trip\n\n**Food:** Ramen, Sushi, Yakitori, Wagyu\n\n**Best time:** March–April (Cherry blossom) or Nov\n\nNeed a Tokyo itinerary?",
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
) -> str:
    """OpenAI / OpenRouter / Ollama — all share the same OpenAI-compatible API."""
    from openai import AsyncOpenAI

    kwargs: dict = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url

    client = AsyncOpenAI(**kwargs)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
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
        system_instruction=SYSTEM_PROMPT,
    )
    chat = gemini_model.start_chat(history=gemini_history)
    response = await chat.send_message_async(last_message)
    return response.text.strip()


async def _call_claude(
    history: List[Dict[str, str]],
    api_key: str,
    model: str,
) -> str:
    """Anthropic Claude via anthropic SDK."""
    from anthropic import AsyncAnthropic

    client = AsyncAnthropic(api_key=api_key)
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    response = await client.messages.create(
        model=model,
        system=SYSTEM_PROMPT,
        messages=messages,
        max_tokens=800,
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Fallback (rule-based)
# ---------------------------------------------------------------------------

def _rule_based_reply(user_message: str) -> str | None:
    msg = user_message.lower().strip()
    for key, value in FALLBACK_RESPONSES.items():
        if key in msg:
            return value
    if any(w in msg for w in ["du lịch", "travel", "trip", "tour", "hotel", "khách sạn"]):
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

    # Fallback: rule-based
    last_user_msg = next(
        (m["content"] for m in reversed(history) if m["role"] == "user"), ""
    )
    reply = _rule_based_reply(last_user_msg)
    if reply:
        return reply

    return (
        "Xin lỗi, tôi chưa có thông tin về chủ đề này. 😊\n\n"
        "Tôi có thể tư vấn về các điểm đến phổ biến như:\n"
        "🇻🇳 **Việt Nam:** Hà Nội, Đà Nẵng, Hội An, Sapa, Phú Quốc\n"
        "🌏 **Châu Á:** Bangkok, Tokyo, Bali, Singapore\n"
        "🌍 **Châu Âu:** Paris, Rome, Barcelona\n\n"
        "Bạn muốn khám phá điểm đến nào?"
    )

