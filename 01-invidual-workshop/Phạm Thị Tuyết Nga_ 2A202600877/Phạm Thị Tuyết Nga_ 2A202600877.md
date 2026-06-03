# Workshop — Mổ App AI Thật

**Họ tên:** Phạm Thị Tuyết Nga  
**MSSV:** 2A202600877  
**Thời gian:** 35-45 phút  
**Hình thức:** cá nhân trước, chia sẻ theo nhóm sau  
**Output:** finding note + sketch `as-is / to-be`

Mục tiêu không phải chấm "UI đẹp hay xấu". Mục tiêu là dùng sản phẩm thật như một bài needfinding: tìm chỗ product gãy trong workflow thật, rồi viết finding đó thành quyết định product.

---

## 1. Chọn một sản phẩm để dùng thử

| Sản phẩm | AI feature | Cách truy cập |
|---|---|---|
| **MoMo — Trợ lý AI**  | Trợ lý chatbot trong ví, tra cứu giao dịch, gợi ý chi tiêu, hỏi đáp dịch vụ | App MoMo (ví điện tử — M_Service) |

**Mô tả:** MoMo là siêu ứng dụng ví điện tử lớn nhất Việt Nam, tích hợp thanh toán, chuyển tiền, trả góp, đầu tư, mua sắm. Trợ lý AI trong MoMo được quảng bá là hiểu được nhu cầu tài chính của user, trả lời câu hỏi về giao dịch, gợi ý quản lý chi tiêu và hỗ trợ thao tác ngay trong app.

---

## 2. Dùng thử: promise vs reality

**Product hứa gì?**  
Trợ lý tài chính thông minh hiểu lịch sử giao dịch của user — trả lời được "tôi tiêu bao nhiêu", gợi ý tiết kiệm, hỗ trợ thao tác chuyển tiền/thanh toán và xử lý vấn đề ngay trong 1 cửa sổ chat.

**User nào được hứa sẽ được giúp?**  
Người dùng MoMo cần quản lý chi tiêu, người bận muốn thao tác nhanh bằng hội thoại, người gặp sự cố giao dịch cần hỗ trợ tức thì.

**Kỳ vọng AI làm được task nào?**
- Tổng hợp chi tiêu cá nhân theo danh mục/thời gian
- Thực hiện thao tác có hậu quả (chuyển tiền, đặt lịch nhắc, hủy gói trả góp)
- Xử lý khiếu nại giao dịch lạ với context đơn hàng thật

**Điểm gãy quan sát được:**

### Query 1: Hỏi thông tin chi tiêu cá nhân
> **"Tháng này tôi tiêu bao nhiêu cho ăn uống?"**

| | |
|---|---|
| **Kỳ vọng** | Tổng hợp số tiền theo danh mục "ăn uống" từ lịch sử giao dịch thật |
| **Thực tế** | Trợ lý trả lời chung chung về tính năng "Quản lý chi tiêu", hướng dẫn user tự vào mục Thống kê xem, không tự tổng hợp con số |
| **Điểm gãy** | ❌ Failure — không đọc/tổng hợp dữ liệu giao dịch thật, đẩy việc về cho user |

### Query 2: Multi-intent + action có hậu quả
> **"Chuyển 500k cho số 09xx và nhắc tôi chuyển lại vào mùng 1 hàng tháng"**

| | |
|---|---|
| **Kỳ vọng** | Mở luồng chuyển tiền điền sẵn số + số tiền, đồng thời tạo nhắc định kỳ |
| **Thực tế** | Trợ lý chỉ gợi link "Chuyển tiền", không điền sẵn thông tin, bỏ qua phần "nhắc định kỳ" — user phải tự thao tác lại từ đầu |
| **Điểm gãy** | ⚠️ Low-confidence → tách nhỏ intent thất bại → không có action thật |

### Query 3: Khiếu nại giao dịch lạ (action + áp lực thời gian)
> **"Tôi bị trừ 200k giao dịch lạ tối qua, không phải tôi, giờ làm sao?"**

| | |
|---|---|
| **Kỳ vọng** | Kéo giao dịch thật → xác nhận → mở luồng khiếu nại/khóa thẻ ngay |
| **Thực tế** | Trả về quy trình khiếu nại chung chung, yêu cầu user tự chụp màn hình + gọi tổng đài 1900, chờ xử lý 3–5 ngày |
| **Điểm gãy** | 🔴 Action gap + Time pressure — biết quy trình nhưng không làm được gì, tiền đang ở rủi ro |

---

## 3. Vẽ 4 paths

| Path | Quan sát thực tế trong Trợ lý MoMo |
|---|---|
| **Happy** | Khi hỏi thông tin công khai (cách nạp tiền, phí dịch vụ, khuyến mãi đang chạy) → trợ lý trả lời đúng, nhanh ✅ |
| **Low-confidence** | Khi query gồm nhiều ý hoặc cần thao tác → trợ lý chỉ gợi link chung, không hỏi lại để làm rõ ⚠️ |
| **Failure** | Khi cần dữ liệu giao dịch thật của user (chi tiêu, số dư danh mục) → trợ lý không truy cập, đẩy user tự xem ❌ |
| **Correction** | Khi user nói lại/bổ sung context → trợ lý không nhớ hội thoại trước, bắt user gõ lại từ đầu 🔴 |

```
User gõ/nói câu hỏi cho Trợ lý
        │
        ▼
Trợ lý AI nhận input
        │
        ├─ [Happy path] ──────────────────────► Hiểu đúng intent → Trả lời ✅
        │
        ├─ [Low-confidence] ──────────────────► Gợi link chung chung ⚠️
        │                                        Không hỏi lại, không điền sẵn
        │
        ├─ [Cần data giao dịch thật] ─────────► "Bạn vào mục Thống kê xem" ❌
        │                                        Không tự tổng hợp con số
        │
        └─ [Cần thực hiện action] ────────────► "Gọi 1900 / tự thao tác" 🔴
                                                 User tự xử, chờ 3–5 ngày
```

**User bị kẹt nhiều nhất tại:** Bước "Cần data thật" và "Cần action" — Trợ lý chỉ là FAQ thông minh, không kết nối được lịch sử giao dịch và không thực hiện được thao tác thật.

---

## 4. Viết finding thành quyết định

**Finding 1 — Data gap:**

```
Khi user hỏi về chi tiêu cá nhân ("tháng này tiêu bao nhiêu cho ăn uống"),
Trợ lý không truy cập/tổng hợp lịch sử giao dịch thật nên trả lời chung chung và đẩy user tự xem,
hậu quả là trợ lý không có giá trị gì hơn việc user tự bấm vào mục Thống kê.
Lỗi thuộc layer data-tool: thiếu kết nối tới dữ liệu giao dịch đã phân loại của user.
Nên sửa bằng: cho trợ lý đọc read-only lịch sử giao dịch (sau xác thực),
tổng hợp theo danh mục/thời gian và trả lời thẳng con số kèm biểu đồ.
```

**Finding 2 — Action gap + Time pressure (case ưu tiên):**

```
Khi user báo giao dịch lạ và hỏi cách xử lý,
Trợ lý trả về quy trình chung thay vì kéo giao dịch thật và mở luồng xử lý,
hậu quả là user phải tự chụp màn hình, gọi tổng đài, chờ 3–5 ngày — trong khi tiền đang ở rủi ro.
Lỗi thuộc layer data-tool + UX recovery: không có truy vấn giao dịch, không có action khẩn cấp.
Nên sửa bằng: cho trợ lý kéo giao dịch nghi vấn, hiển thị chi tiết,
thêm nút [Khóa nguồn tiền tạm thời] + [Gửi khiếu nại] điền sẵn context,
và handoff sang nhân viên với đầy đủ thông tin nếu cần.
```

**Finding 3 — Low-confidence không có clarification:**

```
Khi user gửi yêu cầu nhiều ý ("chuyển 500k cho số X và nhắc tôi mỗi tháng"),
Trợ lý không tách intent và không hỏi lại mà chỉ gợi 1 link chung,
hậu quả là user nhận kết quả không khớp yêu cầu, phải thao tác thủ công lại từ đầu.
Lỗi thuộc layer intent + UX recovery.
Nên sửa bằng low-confidence path: detect multi-intent → xác nhận từng phần
(số tiền, người nhận, lịch nhắc) → điền sẵn luồng chuyển tiền + tạo nhắc định kỳ.
```

---

## 5. Sketch as-is / to-be

### As-is (flow hiện tại)

```
User: "Tôi bị trừ 200k giao dịch lạ tối qua, giờ làm sao?"
        │
        ▼
Trợ lý xử lý text
        │
        ▼
Tìm trong knowledge base về quy trình khiếu nại
        │
        ▼
Trả về: "Bạn chụp màn hình giao dịch và gọi 1900 5454 41"  ⚠️ [Quy trình chung, không kéo giao dịch thật]
        │
        ▼
Quick buttons: [Xem hướng dẫn] [Gọi tổng đài] [Câu hỏi thường gặp]  ❌ [Không có action thật]
        │
        ▼
User tự chụp màn hình → gọi tổng đài → chờ 3–5 ngày  🔴 [Time pressure: tiền đang ở rủi ro]
```

**Điểm gãy:** Không truy vấn được giao dịch → không xác nhận được → không có action khẩn → đẩy sang tổng đài.

---

### To-be (flow đề xuất)

```
User: "Tôi bị trừ 200k giao dịch lạ tối qua, giờ làm sao?"
        │
        ▼
Trợ lý kéo giao dịch gần nhất của user (sau xác thực)
        │
        ▼
Hiển thị: GD -200.000đ · 22:14 hôm qua · Merchant "ABC123"
          ⚠️ Nghi vấn: thiết bị lạ / địa điểm bất thường
        │
        ▼
Trợ lý hỏi lại: "Đây có phải giao dịch bạn thực hiện không?"
        │
        ├─ [Không phải tôi] → [Khóa nguồn tiền tạm thời] (confirm 2 bước) → Mở khiếu nại điền sẵn ✅
        │                      → Gửi mã tra soát + thời hạn xử lý dự kiến
        │
        └─ [Cần hỗ trợ thêm] → Connect nhân viên với full context giao dịch ✅
                                (user không phải kể lại từ đầu)
```

**So sánh chi tiết As-Is vs To-Be:**

| Yếu tố | As-Is | To-Be |
|---|---|---|
| **Source dữ liệu** | Quy trình chung từ knowledge base | Kéo giao dịch thật của user |
| **Xác nhận giao dịch** | Không có | Hiển thị chi tiết + cờ nghi vấn |
| **Clarification** | Không hỏi lại | Hỏi "có phải bạn thực hiện không" |
| **Action button** | Generic (Hướng dẫn, Tổng đài) | [Khóa tạm thời] [Gửi khiếu nại điền sẵn] |
| **Confirm trước action** | Không có | Confirm 2 bước trước khi khóa |
| **Time alert** | Không có | Cảnh báo rủi ro + thời hạn tra soát |
| **Handoff sang nhân viên** | "Gọi 1900, chờ 3–5 ngày" | Connect thẳng với full context |
| **Correction log** | Không lưu | Ghi nhận query fail để cải thiện model |

---

## 6. Tự kiểm trước khi nộp

- [x] Có ít nhất 1 screenshot hoặc observation cụ thể — 3 query thật với input/output quan sát được.
- [x] Có đủ 4 paths — Happy ✅ / Low-confidence ⚠️ / Failure ❌ / Correction 🔴 đều có observation.
- [x] Finding được viết thành product decision theo format chuẩn, không chỉ là nhận xét.
- [x] Sketch có as-is và to-be với flow chi tiết, đánh dấu điểm gãy và điểm sửa.
- [x] Finding sẽ đổi SPEC: **kết nối Trợ lý MoMo với dữ liệu giao dịch thật** để đọc lịch sử, tổng hợp chi tiêu, và thực hiện action (khóa tiền, khiếu nại, chuyển tiền điền sẵn) với confirmation 2 bước + time alert — thay vì đẩy toàn bộ về tổng đài và chờ 3–5 ngày.

---

## Product Decision

> **"Trợ lý MoMo hiện chỉ là FAQ thông minh — biết quy trình nhưng không truy cập được dữ liệu giao dịch thật của user và không thực hiện được action nào. Ưu tiên sửa: kết nối trợ lý với lịch sử giao dịch để đọc và tổng hợp chi tiêu chính xác theo context, và cho phép thực hiện action có hậu quả (khóa nguồn tiền, gửi khiếu nại điền sẵn, chuyển tiền) với confirmation 2 bước + time alert, thay vì đẩy toàn bộ sang tổng đài và chờ 3–5 ngày."**
