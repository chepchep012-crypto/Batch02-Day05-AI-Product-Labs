"""
SQLite database for Travel Chatbot bookings.
Table: bookings
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookings.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at    TEXT    NOT NULL,
            city          TEXT    NOT NULL,
            hotel_name    TEXT    NOT NULL,
            room_type     TEXT    NOT NULL,
            guest_name    TEXT    DEFAULT '',
            phone         TEXT    DEFAULT '',
            email         TEXT    DEFAULT '',
            checkin       TEXT    DEFAULT '',
            checkout      TEXT    DEFAULT '',
            num_guests    INTEGER DEFAULT 1,
            status        TEXT    DEFAULT 'pending',
            notes         TEXT    DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


def create_booking(data: Dict) -> int:
    """Insert a new booking and return its id."""
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO bookings
           (created_at, city, hotel_name, room_type, guest_name, phone, email,
            checkin, checkout, num_guests, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            datetime.now().isoformat(timespec="seconds"),
            data.get("city", ""),
            data.get("hotel_name", ""),
            data.get("room_type", ""),
            data.get("guest_name", ""),
            data.get("phone", ""),
            data.get("email", ""),
            data.get("checkin", ""),
            data.get("checkout", ""),
            int(data.get("num_guests", 1)),
            data.get("notes", ""),
        ),
    )
    conn.commit()
    booking_id = cur.lastrowid
    conn.close()
    return booking_id


def list_bookings(limit: int = 200) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM bookings ORDER BY created_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_booking(booking_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_booking_status(booking_id: int, status: str) -> bool:
    conn = get_connection()
    conn.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    conn.commit()
    changed = conn.total_changes > 0
    conn.close()
    return changed
