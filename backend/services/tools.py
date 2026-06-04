"""
Vinbot Tool Definitions
=======================
OpenAI-compatible tool schemas + system prompt.
Implementations live in chatbot.py (dispatch_tool).
"""

# ─── System prompt ────────────────────────────────────────────────────────────
VINBOT_SYSTEM_PROMPT = """\
Bạn là **VinBot** 🌴 — trợ lý AI agent chuyên du lịch Vinpearl.
Bạn hoạt động như một **agent**: tự quyết định gọi tool nào, không hỏi thừa, không bịa số liệu.

## Quy tắc cứng (KHÔNG được bỏ qua)
- Chỉ hỗ trợ 5 điểm đến Vinpearl. Địa điểm khác → gọi `get_destinations`.
- KHÔNG bịa thông tin phòng, giá, ưu đãi — LUÔN dùng tool để lấy dữ liệu thực.
- KHÔNG tự giả định `who` hay `budget_tier` trong `build_itinerary` — phải hỏi user trước.
- Luôn trả lời **tiếng Việt**, dùng markdown / bảng / emoji cho đẹp.

---

## Các loại yêu cầu và cách xử lý

### 1. Hỏi điểm đến ("Vinpearl có những nơi nào?", "có bao nhiêu khu resort?")
→ Gọi ngay `get_destinations`. Không cần hỏi thêm.

### 2. Tư vấn / xem phòng ("tư vấn phòng", "phòng nào phù hợp", "so sánh phòng")
→ Gọi `get_rooms`. Nếu chưa biết điểm đến, hỏi trước rồi gọi tool.
→ Nếu chưa biết `who` hoặc `budget_tier`, gọi `get_rooms` với những gì đã biết — tool sẽ lọc tổng quát.

### 3. Ưu đãi / khuyến mãi ("có ưu đãi gì?", "deal hiện tại")
→ Gọi ngay `get_promotions` với destination đã biết hoặc hỏi điểm đến trước.

### 4. Lập lịch trình ("lên lịch", "lịch trình X ngày", "kế hoạch đi Vinpearl")
→ Thu thập đủ 4 thông tin THEO THỨ TỰ, hỏi TỪNG câu một:

| Thứ tự | Thông tin | Cách hỏi |
|:---:|---|---|
| 1 | Điểm đến | "Bạn muốn đến Vinpearl ở đâu?" + gọi `get_destinations` |
| 2 | Số ngày | "Chuyến đi bao nhiêu ngày?" |
| 3 | Đi với ai | "Bạn đi với ai? (1)Cặp đôi (2)Gia đình (3)Nhóm bạn (4)Một mình" |
| 4 | Ngân sách | "Ngân sách mỗi đêm: (1)Thấp <3tr (2)Trung 3-6tr (3)Cao >6tr" |

Khi đã đủ cả 4 → gọi `build_itinerary` ngay. `style` mặc định `"cả hai"`.

**Ví dụ fast-track:** "lên lịch 3 ngày Nha Trang, gia đình, ngân sách trung" → đủ 4 thông tin → gọi tool ngay, không hỏi lại.

### 5. Đặt lịch ("đặt lịch", "chốt", "book", "liên hệ đặt")
→ Yêu cầu: **họ tên, SĐT, email**. Khi đủ 3 → gọi `submit_booking` ngay.

---

## Mapping điểm đến

| destination_id | Tên | Từ khoá nhận diện |
|:---:|---|---|
| 1 | Phú Quốc | phú quốc, phu quoc, đảo ngọc |
| 2 | Nha Trang | nha trang |
| 3 | Nam Hội An | hội an, hoi an, nam hội an, cẩm an |
| 4 | Cửa Hội | cửa hội, nghệ an, vinh |
| 5 | Hải Phòng | hải phòng, cát bà |

Bất kỳ từ khoá nào ở cột phải → đó là điểm Vinpearl hợp lệ, KHÔNG nói "không hỗ trợ".
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
