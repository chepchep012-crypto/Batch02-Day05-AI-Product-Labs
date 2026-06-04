"""Gửi thông báo booking / liên hệ qua Telegram Bot API."""
import os
from typing import Optional

import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()


def send_telegram_message(text: str, parse_mode: str = "HTML") -> bool:
    """
    Gửi tin nhắn tới chat/group Telegram.
    Cần TELEGRAM_BOT_TOKEN và TELEGRAM_CHAT_ID trong env.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID — bỏ qua gửi tin")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text[:4096],
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("ok"):
                print(f"[Telegram] API error: {data}")
                return False
            return True
    except Exception as e:
        print(f"[Telegram] send error: {e}")
        return False


def format_vp_booking_telegram(booking: dict, booking_id: Optional[int] = None) -> str:
    """Định dạng HTML cho Telegram."""
    lines = ["<b>🆕 Yêu cầu đặt lịch Vinpearl</b>"]
    if booking_id:
        lines.append(f"<b>Mã:</b> #{booking_id:04d}")
    lines.append(f"<b>Điểm đến:</b> {booking.get('city', '—')}")
    lines.append(f"<b>Khách sạn:</b> {booking.get('hotel_name', '—')}")
    lines.append(f"<b>Phòng:</b> {booking.get('room_type', '—')}")
    lines.append(f"<b>Họ tên:</b> {booking.get('guest_name', '—')}")
    lines.append(f"<b>SĐT:</b> {booking.get('phone', '—')}")
    lines.append(f"<b>Email:</b> {booking.get('email', '—')}")
    if booking.get("checkin"):
        lines.append(f"<b>Check-in:</b> {booking['checkin']}")
    if booking.get("checkout"):
        lines.append(f"<b>Check-out:</b> {booking['checkout']}")
    lines.append(f"<b>Số khách:</b> {booking.get('num_guests', 1)}")
    if booking.get("notes"):
        lines.append(f"<b>Ghi chú:</b> {booking['notes']}")
    return "\n".join(lines)
