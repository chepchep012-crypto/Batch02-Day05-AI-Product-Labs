from __future__ import annotations


def submit_booking(
    guest_name: str,
    phone: str,
    email: str,
    destination_name: str = "",
    room_type: str = "",
    resort_name: str = "Vinpearl",
    checkin: str = "",
    checkout: str = "",
    num_guests: int = 2,
    notes: str = "",
) -> str:
    """Save booking request to DB and notify CSKH via Telegram."""
    try:
        from database import create_booking
        from services.telegram_notify import format_vp_booking_telegram, send_telegram_message

        booking_data = {
            "city":        destination_name,
            "hotel_name":  resort_name,
            "room_type":   room_type,
            "guest_name":  guest_name,
            "phone":       phone,
            "email":       email,
            "checkin":     checkin,
            "checkout":    checkout,
            "num_guests":  num_guests,
            "notes":       notes,
        }
        booking_id = None
        telegram_ok = False
        try:
            booking_id = create_booking(booking_data)
        except Exception as e:
            print(f"[DB] create_booking: {e}")
        try:
            telegram_ok = send_telegram_message(
                format_vp_booking_telegram(booking_data, booking_id)
            )
        except Exception as e:
            print(f"[Telegram] notify: {e}")

        id_label = f"`#{booking_id:04d}`" if booking_id else "`#---`"
        tg_line  = "📲 Đã gửi thông báo tới nhóm CSKH trên Telegram.\n" if telegram_ok else ""
        return (
            f"✅ **Yêu cầu đặt lịch Vinpearl {destination_name}** — {id_label}\n\n"
            f"| Thông tin | Chi tiết |\n|---|---|\n"
            f"| 👤 Họ tên | {guest_name} |\n"
            f"| 📞 SĐT | {phone} |\n"
            f"| 📧 Email | {email} |\n"
            f"| 🏨 Phòng | {room_type or 'Theo gợi ý'} |\n\n"
            f"{tg_line}"
            "Nhân viên CSKH sẽ liên hệ bạn trong vòng **24 giờ** để xác nhận và tư vấn thêm. 🌴"
        )
    except Exception as exc:
        return f"Lỗi đặt lịch: {exc}"
