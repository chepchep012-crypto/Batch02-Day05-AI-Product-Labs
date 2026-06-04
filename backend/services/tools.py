"""
Vinbot Tool Definitions
=======================
OpenAI-compatible tool schemas + system prompt.
Implementations live in chatbot.py (dispatch_tool).
"""

# ─── System prompt ────────────────────────────────────────────────────────────
VINBOT_SYSTEM_PROMPT = """\
Bạn là **VinBot** 🌴 — trợ lý AI chuyên lập kế hoạch du lịch Vinpearl.

## Quy tắc
- Chỉ hỗ trợ 5 điểm đến Vinpearl: **Phú Quốc**, **Nha Trang**, **Nam Hội An**, **Cửa Hội (Nghệ An)**, **Hải Phòng**.
- Khi người dùng hỏi về địa điểm khác → gọi `get_destinations` và hướng họ về các điểm Vinpearl.
- Luôn trả lời bằng **tiếng Việt**, thân thiện, ngắn gọn, dùng markdown/bảng/emoji cho dễ đọc.
- KHÔNG bịa thông tin phòng, giá, ưu đãi — luôn dùng tool để lấy dữ liệu thật.

## Luồng lập lịch trình
1. Xác định: điểm đến, số ngày, đối tượng đi (`who`), ngân sách (`budget_tier`).
2. Nếu thiếu thông tin quan trọng → hỏi ngắn gọn, **tối đa 1 câu hỏi mỗi lượt**.
3. Khi đã có đủ điểm đến + số ngày + who + budget → gọi **`build_itinerary`** ngay.
4. `style` (phong cách) không bắt buộc — dùng `"cả hai"` nếu không đề cập.
5. Sau khi trả lịch trình, hỏi xem user có muốn thay đổi gì không.

## Luồng đặt lịch
1. Khi user nói "đặt lịch" / "chốt" / "book" → yêu cầu: **họ tên, SĐT, email**.
2. Khi đủ 3 thông tin → gọi **`submit_booking`** ngay.
3. Xác nhận đã gửi và CSKH sẽ liên hệ lại.

## Mapping điểm đến
| Tên | destination_id |
|---|:---:|
| Phú Quốc | 1 |
| Nha Trang | 2 |
| Nam Hội An / Hội An | 3 |
| Cửa Hội / Nghệ An | 4 |
| Hải Phòng | 5 |
"""

# ─── Tool schemas (OpenAI function-calling format) ────────────────────────────
VINBOT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_destinations",
            "description": "Trả về danh sách 5 điểm đến Vinpearl mà VinBot hỗ trợ.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_rooms",
            "description": (
                "Lấy danh sách phòng Vinpearl tại một điểm đến, lọc theo đối tượng, ngân sách, phong cách. "
                "Trả về bảng so sánh phòng để user chọn."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_id": {
                        "type": "integer",
                        "description": "ID điểm đến (1=Phú Quốc, 2=Nha Trang, 3=Nam Hội An, 4=Cửa Hội, 5=Hải Phòng)",
                    },
                    "who": {
                        "type": "string",
                        "enum": ["solo", "couple", "family", "group"],
                        "description": "Đối tượng: solo=1 mình, couple=cặp đôi, family=gia đình, group=nhóm bạn",
                    },
                    "budget_tier": {
                        "type": "string",
                        "enum": ["thấp", "trung", "cao"],
                        "description": "Ngân sách/đêm: thấp<3tr, trung=3-6tr, cao>6tr",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["biển", "vui chơi", "cả hai"],
                        "description": "Phong cách chuyến đi",
                    },
                },
                "required": ["destination_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_promotions",
            "description": "Lấy danh sách ưu đãi / khuyến mãi Vinpearl đang áp dụng tại điểm đến.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_id": {
                        "type": "integer",
                        "description": "ID điểm đến",
                    }
                },
                "required": ["destination_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "build_itinerary",
            "description": (
                "Xây dựng lịch trình Vinpearl hoàn chỉnh: timeline theo ngày, gợi ý phòng tốt nhất, "
                "bảng so sánh ≥5 phòng, ưu đãi đang áp dụng, và chi phí ước tính. "
                "Gọi ngay khi đã biết đủ: điểm đến + số ngày + who + budget_tier."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "destination_id": {"type": "integer"},
                    "destination_name": {"type": "string", "description": "Tên hiển thị, vd: 'Phú Quốc'"},
                    "days": {"type": "integer", "description": "Số ngày (1–14)"},
                    "who": {
                        "type": "string",
                        "enum": ["solo", "couple", "family", "group"],
                    },
                    "budget_tier": {
                        "type": "string",
                        "enum": ["thấp", "trung", "cao"],
                    },
                    "style": {
                        "type": "string",
                        "enum": ["biển", "vui chơi", "cả hai"],
                        "description": "Nếu không rõ, dùng 'cả hai'",
                    },
                },
                "required": ["destination_id", "destination_name", "days", "who", "budget_tier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_booking",
            "description": (
                "Lưu yêu cầu đặt lịch vào database và gửi thông báo tới CSKH qua Telegram. "
                "Chỉ gọi khi user đã cung cấp đủ: họ tên + số điện thoại + email."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "guest_name": {"type": "string", "description": "Họ tên đầy đủ"},
                    "phone": {"type": "string", "description": "Số điện thoại"},
                    "email": {"type": "string", "description": "Email"},
                    "destination_name": {"type": "string"},
                    "room_type": {"type": "string"},
                    "resort_name": {"type": "string"},
                    "checkin": {"type": "string", "description": "dd/mm/yyyy, bỏ trống nếu chưa biết"},
                    "checkout": {"type": "string"},
                    "num_guests": {"type": "integer"},
                    "notes": {"type": "string"},
                },
                "required": ["guest_name", "phone", "email", "destination_name"],
            },
        },
    },
]
