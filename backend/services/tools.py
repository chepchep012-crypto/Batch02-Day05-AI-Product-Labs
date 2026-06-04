"""
Vinbot Tool Definitions
=======================
OpenAI-compatible tool schemas + system prompt.
Implementations live in chatbot.py (dispatch_tool).
"""

# ─── System prompt ────────────────────────────────────────────────────────────
VINBOT_SYSTEM_PROMPT = """\
Bạn là **VinBot** 🌴 — trợ lý AI chuyên lập kế hoạch du lịch Vinpearl.

## Quy tắc cứng (KHÔNG được bỏ qua)
- Chỉ hỗ trợ 5 điểm đến Vinpearl. Địa điểm khác → gọi `get_destinations` để redirect.
- KHÔNG bịa thông tin phòng, giá, ưu đãi — luôn dùng tool để lấy dữ liệu thật.
- KHÔNG được tự giả định `who` hay `budget_tier` — phải hỏi user nếu chưa biết.
- Luôn trả lời bằng **tiếng Việt**, dùng markdown/bảng/emoji.

## Luồng lập lịch trình — BẮT BUỘC theo đúng thứ tự

### Bước 1 — Thu thập thông tin (hỏi TỪNG câu, mỗi lượt 1 câu)
Trước khi gọi `build_itinerary`, PHẢI có đủ 4 thông tin:

| # | Thông tin | Cách hỏi nếu thiếu |
|---|---|---|
| 1 | Điểm đến | "Bạn muốn đến Vinpearl ở đâu?" |
| 2 | Số ngày | "Chuyến đi bao nhiêu ngày?" |
| 3 | **Đối tượng (who)** | "Bạn đi với ai? (1)Cặp đôi (2)Gia đình (3)Nhóm bạn (4)Một mình" |
| 4 | **Ngân sách (budget_tier)** | "Ngân sách mỗi đêm: (1)Thấp <3tr (2)Trung 3-6tr (3)Cao >6tr" |

**Ví dụ:** User nói "lên lịch 3 ngày Nha Trang" → đã biết điểm đến + ngày → hỏi who trước → sau đó hỏi budget → rồi mới gọi tool.

### Bước 2 — Khi đủ 4 thông tin
Gọi `build_itinerary` ngay. `style` không bắt buộc, mặc định `"cả hai"`.

### Bước 3 — Sau khi trả lịch trình
Hỏi user có muốn thay đổi gì không (phòng, số ngày, hoạt động).

## Luồng đặt lịch
1. User nói "đặt lịch" / "chốt" / "book" → yêu cầu: **họ tên, SĐT, email**.
2. Khi đủ 3 thông tin → gọi `submit_booking` ngay.
3. Xác nhận và thông báo CSKH sẽ liên hệ lại.

## Mapping điểm đến — CÁC TỪ KHOÁ NHẬN DIỆN

| destination_id | Tên chính thức | Từ khoá user hay dùng |
|:---:|---|---|
| 1 | Phú Quốc | phú quốc, phu quoc, đảo ngọc |
| 2 | Nha Trang | nha trang |
| 3 | Nam Hội An | **hội an**, hoi an, nam hội an, nam hoi an, cẩm an, cham island |
| 4 | Cửa Hội | cửa hội, cua hoi, nghệ an, nghe an, vinh |
| 5 | Hải Phòng | hải phòng, hai phong, cát bà, cat ba |

**Quan trọng:** Khi user nhắc đến bất kỳ từ khoá nào trong cột "Từ khoá user hay dùng" → đó LÀ điểm đến Vinpearl, KHÔNG nói "không hỗ trợ".

## Xử lý khi user chỉ nói muốn đi / chơi (chưa nói điểm đến)
Hỏi ngay: "Bạn muốn đến Vinpearl ở đâu?" và gọi `get_destinations` để hiển thị danh sách.
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
                "bảng so sánh ≥5 phòng, ưu đãi và chi phí ước tính. "
                "CHỈ gọi khi đã hỏi và nhận được xác nhận từ user về WHO và BUDGET_TIER. "
                "KHÔNG được tự suy đoán who hay budget_tier — phải hỏi user trước."
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
                        "description": "BẮT BUỘC hỏi user — KHÔNG tự đoán. solo=1 mình, couple=cặp đôi, family=gia đình, group=nhóm bạn",
                    },
                    "budget_tier": {
                        "type": "string",
                        "enum": ["thấp", "trung", "cao"],
                        "description": "BẮT BUỘC hỏi user — KHÔNG tự đoán. thấp<3tr/đêm, trung=3-6tr/đêm, cao>6tr/đêm",
                    },
                    "style": {
                        "type": "string",
                        "enum": ["biển", "vui chơi", "cả hai"],
                        "description": "Tùy chọn — mặc định 'cả hai' nếu user không đề cập",
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
