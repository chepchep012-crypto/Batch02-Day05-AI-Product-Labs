"""
PostgreSQL / SQLite database for Travel Chatbot bookings.
Uses PostgreSQL when DATABASE_URL env var is set (docker-compose),
falls back to SQLite for local dev without Docker.
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

DATABASE_URL = os.getenv("DATABASE_URL", "")
_USE_PG = bool(DATABASE_URL)


# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

def _pg_conn():
    import psycopg2
    return psycopg2.connect(DATABASE_URL)


def _sqlite_conn() -> sqlite3.Connection:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookings.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create bookings table if it does not exist."""
    ddl = """
        CREATE TABLE IF NOT EXISTS bookings (
            id            SERIAL PRIMARY KEY,
            created_at    TEXT    NOT NULL,
            city          TEXT    NOT NULL DEFAULT '',
            hotel_name    TEXT    NOT NULL DEFAULT '',
            room_type     TEXT    NOT NULL DEFAULT '',
            guest_name    TEXT    DEFAULT '',
            phone         TEXT    DEFAULT '',
            email         TEXT    DEFAULT '',
            checkin       TEXT    DEFAULT '',
            checkout      TEXT    DEFAULT '',
            num_guests    INTEGER DEFAULT 1,
            status        TEXT    DEFAULT 'pending',
            notes         TEXT    DEFAULT ''
        )
    """
    if _USE_PG:
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute(ddl)
        conn.commit()
        cur.close()
        conn.close()
    else:
        sqlite_ddl = ddl.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        conn = _sqlite_conn()
        conn.execute(sqlite_ddl)
        conn.commit()
        conn.close()
    print(f"[DB] init_db ok — backend: {'PostgreSQL' if _USE_PG else 'SQLite'}")


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_booking(data: Dict) -> int:
    sql = """
        INSERT INTO bookings
          (created_at, city, hotel_name, room_type, guest_name, phone, email,
           checkin, checkout, num_guests, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """
    params = (
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
    )
    if _USE_PG:
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        booking_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
    else:
        sqlite_sql = sql.replace("%s", "?").replace("\n        RETURNING id", "")
        conn = _sqlite_conn()
        cur = conn.execute(sqlite_sql, params)
        booking_id = cur.lastrowid
        conn.commit()
        conn.close()
    return booking_id


def list_bookings(limit: int = 200) -> List[Dict]:
    sql = "SELECT * FROM bookings ORDER BY created_at DESC LIMIT %s"
    if _USE_PG:
        import psycopg2.extras
        conn = _pg_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        conn.close()
    else:
        conn = _sqlite_conn()
        rows = [dict(r) for r in conn.execute(sql.replace("%s", "?"), (limit,)).fetchall()]
        conn.close()
    return rows


def get_booking(booking_id: int) -> Optional[Dict]:
    sql = "SELECT * FROM bookings WHERE id = %s"
    if _USE_PG:
        import psycopg2.extras
        conn = _pg_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql, (booking_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return dict(row) if row else None
    else:
        conn = _sqlite_conn()
        row = conn.execute(sql.replace("%s", "?"), (booking_id,)).fetchone()
        conn.close()
        return dict(row) if row else None


def update_booking_status(booking_id: int, status: str) -> bool:
    sql = "UPDATE bookings SET status = %s WHERE id = %s"
    if _USE_PG:
        conn = _pg_conn()
        cur = conn.cursor()
        cur.execute(sql, (status, booking_id))
        changed = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
    else:
        conn = _sqlite_conn()
        conn.execute(sql.replace("%s", "?"), (status, booking_id))
        conn.commit()
        changed = conn.total_changes > 0
        conn.close()
    return changed


# ---------------------------------------------------------------------------
# VINPEARL PLANNING — Room / Promotion tables (SQLite only)
# ---------------------------------------------------------------------------

def init_vinpearl_db() -> None:
    """Create Vinpearl planning tables if they don't exist (SQLite)."""
    conn = _sqlite_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vp_destination (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            province    TEXT    NOT NULL,
            region      TEXT    NOT NULL,
            best_months TEXT,
            is_active   INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS vp_resort (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id  INTEGER NOT NULL,
            name            TEXT    NOT NULL,
            code            TEXT    NOT NULL UNIQUE,
            resort_type     TEXT    NOT NULL,
            address         TEXT,
            amenities       TEXT,
            source_url      TEXT    NOT NULL,
            is_active       INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS vp_room (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            resort_id           INTEGER NOT NULL,
            name                TEXT    NOT NULL,
            capacity_adults     INTEGER NOT NULL DEFAULT 2,
            capacity_children   INTEGER NOT NULL DEFAULT 0,
            view_type           TEXT,
            suitable_for        TEXT,
            budget_level        TEXT    NOT NULL,
            price_per_night     REAL    NOT NULL,
            breakfast_included  INTEGER NOT NULL DEFAULT 0,
            source_url          TEXT    NOT NULL,
            highlights          TEXT,
            is_active           INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS vp_promotion (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            destination_id  INTEGER,
            resort_id       INTEGER,
            name            TEXT    NOT NULL,
            discount_type   TEXT    NOT NULL,
            discount_value  REAL    NOT NULL,
            valid_from      TEXT    NOT NULL,
            valid_to        TEXT    NOT NULL,
            min_nights      INTEGER NOT NULL DEFAULT 1,
            conditions      TEXT,
            source_url      TEXT    NOT NULL,
            is_verified     INTEGER NOT NULL DEFAULT 1,
            is_active       INTEGER NOT NULL DEFAULT 1
        );
    """)
    conn.commit()
    conn.close()
    print("[DB] Vinpearl tables ready")


def _is_vinpearl_seeded() -> bool:
    try:
        conn = _sqlite_conn()
        count = conn.execute("SELECT COUNT(*) FROM vp_destination").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def seed_vinpearl_data() -> None:
    """Insert Vinpearl seed data (from vinpearl_itinerary.sql) if tables are empty."""
    if _is_vinpearl_seeded():
        return

    conn = _sqlite_conn()

    conn.executemany(
        "INSERT INTO vp_destination (name, province, region, best_months) VALUES (?,?,?,?)",
        [
            ("Phú Quốc",   "Kiên Giang", "south",   "11-4"),
            ("Nha Trang",  "Khánh Hòa",  "central", "1-8"),
            ("Nam Hội An", "Quảng Nam",  "central", "2-7"),
            ("Cửa Hội",   "Nghệ An",    "central", "5-8"),
            ("Hải Phòng",  "Hải Phòng",  "north",   "4-10"),
        ],
    )

    conn.executemany(
        "INSERT INTO vp_resort (destination_id, name, code, resort_type, address, amenities, source_url) VALUES (?,?,?,?,?,?,?)",
        [
            (1, "Vinpearl Resort & Spa Phú Quốc",   "VPR_PQ",   "resort",      "Bãi Dài, Gành Dầu, Phú Quốc",   "Bãi biển riêng, 5 hồ bơi, Spa 5 sao, 6 nhà hàng",          "https://vinpearl.com/vi/resort-spa-phu-quoc"),
            (1, "Vinpearl Discovery 1 Phú Quốc",    "VPD1_PQ",  "discovery",   "Gành Dầu, Phú Quốc",             "Bungalow gần biển, hồ bơi vô cực, xe đạp miễn phí",         "https://vinpearl.com/vi/discovery-1-phu-quoc"),
            (1, "Vinpearl Grand World Phú Quốc",    "VPGW_PQ",  "grand_world", "Bãi Dài, Phú Quốc",              "Condotel cao cấp, khu Grand World 4 mùa, casino",            "https://vinpearl.com/vi/grand-world-phu-quoc"),
            (1, "Vinpearl Safari Resort Phú Quốc",  "VPSR_PQ",  "safari",      "Khu Safari, Phú Quốc",           "Bungalow trong rừng, hồ bơi thiên nhiên, tour safari riêng", "https://vinpearl.com/vi/safari-resort-phu-quoc"),
            (2, "Vinpearl Resort & Spa Nha Trang",  "VPR_NT",   "resort",      "Đảo Hòn Tre, Nha Trang",         "Bãi biển riêng, 3 hồ bơi, Spa, cáp treo vào đảo",          "https://vinpearl.com/vi/resort-spa-nha-trang"),
            (2, "Vinpearl Luxury Nha Trang",        "VPL_NT",   "resort",      "Đảo Hòn Tre, Nha Trang",         "Hồ bơi riêng mỗi villa, butler 24/7, Spa cao cấp",           "https://vinpearl.com/vi/luxury-nha-trang"),
            (3, "Vinpearl Nam Hội An",              "VP_NHA",   "resort",      "Tây An, Duy Xuyên, Quảng Nam",   "Bãi biển riêng 3.5km, 4 hồ bơi, VinWonders Nam Hội An",     "https://vinpearl.com/vi/nam-hoi-an"),
            (4, "Vinpearl Cửa Hội Resort & Villas", "VP_CH",    "resort",      "Cửa Hội, Nghi Xuân, Nghệ An",   "Bãi biển Cửa Lò sát resort, hồ bơi ngoài trời",             "https://vinpearl.com/vi/cua-hoi"),
            (5, "Vinpearl Resort & Golf Hải Phòng", "VP_HP",    "resort",      "Đảo Vũ Yên, Hải Phòng",          "Sân golf 18 lỗ championship, hồ bơi, bãi biển riêng",       "https://vinpearl.com/vi/hai-phong"),
        ],
    )

    conn.executemany(
        """INSERT INTO vp_room
           (resort_id, name, capacity_adults, capacity_children, view_type, suitable_for,
            budget_level, price_per_night, breakfast_included, source_url, highlights)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        [
            # VPR_PQ (resort_id=1)
            (1, "Deluxe Sea View Phú Quốc",       2, 0, "Biển",     "Cặp đôi, Solo",            "mid",    2800000, 1, "https://vinpearl.com/vi/resort-spa-phu-quoc/phong/deluxe-sea-view",  "View biển trực diện, bể bơi vô cực, gần trung tâm Dương Đông"),
            (1, "Family Suite Phú Quốc",          2, 2, "Vườn",     "Gia đình có trẻ nhỏ",      "mid",    4200000, 1, "https://vinpearl.com/vi/resort-spa-phu-quoc/phong/family-suite",      "Phòng rộng 65m², đầy đủ tiện nghi gia đình, khu vui chơi trẻ em"),
            (1, "Beachfront Pool Villa Phú Quốc", 2, 1, "Biển",     "Cặp đôi",                  "luxury", 7200000, 1, "https://vinpearl.com/vi/resort-spa-phu-quoc/phong/pool-villa",        "Villa hồ bơi riêng, view biển panorama, butler service"),
            # VPD1_PQ (resort_id=2)
            (2, "Discovery Deluxe Bungalow",      2, 0, "Biển",     "Cặp đôi, Nhóm bạn, Solo",  "mid",    2500000, 1, "https://vinpearl.com/vi/discovery-1-phu-quoc/phong/deluxe-bungalow", "Bungalow gần biển, không khí hoang sơ, xe điện miễn phí đến VinWonders"),
            (2, "Discovery Family Bungalow",      2, 2, "Vườn",     "Gia đình có trẻ nhỏ",      "mid",    3600000, 1, "https://vinpearl.com/vi/discovery-1-phu-quoc/phong/family-bungalow", "Bungalow gia đình, gần biển, xe điện miễn phí đến VinWonders"),
            # VPGW_PQ (resort_id=3)
            (3, "Grand World Studio",             2, 0, "Thành phố","Cặp đôi, Solo, Nhóm bạn",  "mid",    2200000, 0, "https://vinpearl.com/vi/grand-world-phu-quoc/phong/studio",           "Trong khu Grand World, đi bộ ra phố đi bộ buổi tối, giá tốt nhất"),
            (3, "Grand World 1BR Suite",          2, 2, "Biển",     "Gia đình, Cặp đôi",         "luxury", 5500000, 1, "https://vinpearl.com/vi/grand-world-phu-quoc/phong/1br-suite",        "Suite cao cấp view biển, gần VinWonders và Grand World, bao gồm bữa sáng"),
            # VPSR_PQ (resort_id=4)
            (4, "Safari Tent Lodge",              2, 1, "Rừng",     "Gia đình, Cặp đôi",         "luxury", 5800000, 1, "https://vinpearl.com/vi/safari-resort-phu-quoc/phong/tent-lodge",    "Lều lodge trong rừng Safari, trải nghiệm độc đáo, gần Safari nhất"),
            (4, "Jungle View Deluxe",             2, 0, "Rừng",     "Cặp đôi, Nhóm bạn",         "mid",    3200000, 1, "https://vinpearl.com/vi/safari-resort-phu-quoc/phong/jungle-view",   "View rừng nhiệt đới, gần Vinpearl Safari, trải nghiệm thiên nhiên"),
            # VPR_NT (resort_id=5)
            (5, "Sea View Deluxe Nha Trang",      2, 0, "Biển",     "Cặp đôi, Solo",              "mid",    2600000, 1, "https://vinpearl.com/vi/resort-spa-nha-trang/phong/sea-view-deluxe", "View biển Nha Trang, gần VinWonders bằng cáp treo miễn phí"),
            (5, "Family Deluxe Nha Trang",        2, 2, "Biển",     "Gia đình có trẻ nhỏ",        "mid",    3800000, 1, "https://vinpearl.com/vi/resort-spa-nha-trang/phong/family-deluxe",   "Phòng gia đình view biển, gần VinWonders Nha Trang và bãi biển riêng"),
            (5, "Premium Suite Nha Trang",        2, 1, "Biển",     "Cặp đôi, Gia đình",          "luxury", 5200000, 1, "https://vinpearl.com/vi/resort-spa-nha-trang/phong/premium-suite",   "Suite cao cấp view biển, butler service, hồ bơi riêng"),
            # VPL_NT (resort_id=6)
            (6, "Luxury Sea View Villa NT",       2, 0, "Biển",     "Cặp đôi",                    "luxury", 7500000, 1, "https://vinpearl.com/vi/luxury-nha-trang/phong/sea-view-villa",      "Villa riêng view biển, butler 24/7, sang trọng nhất Nha Trang"),
            (6, "Luxury Pool Villa NT",           2, 1, "Hồ bơi",   "Cặp đôi, Gia đình nhỏ",     "ultra",  12000000,1, "https://vinpearl.com/vi/luxury-nha-trang/phong/pool-villa",           "Villa hồ bơi riêng, dịch vụ 5 sao hoàn hảo, sang trọng nhất hệ thống"),
            # VP_NHA (resort_id=7)
            (7, "Hội An Deluxe Garden Room",      2, 0, "Vườn",     "Cặp đôi, Solo",              "mid",    2400000, 1, "https://vinpearl.com/vi/nam-hoi-an/phong/deluxe-garden",              "View vườn nhiệt đới, gần phố cổ Hội An 35 phút, biển An Bàng 10 phút xe điện"),
            (7, "Hội An Family Room",             2, 2, "Vườn",     "Gia đình có trẻ nhỏ",        "mid",    3600000, 1, "https://vinpearl.com/vi/nam-hoi-an/phong/family-room",                "Phòng gia đình rộng, gần VinWonders Nam Hội An, biển An Bàng"),
            (7, "Hội An Pool Suite",              2, 1, "Hồ bơi",   "Cặp đôi",                    "luxury", 5200000, 1, "https://vinpearl.com/vi/nam-hoi-an/phong/pool-suite",                 "Suite hồ bơi riêng, sang trọng, gần biển và phố cổ"),
            # VP_CH (resort_id=8)
            (8, "Beach View Deluxe Cửa Hội",     2, 0, "Biển",     "Cặp đôi, Solo",              "mid",    1800000, 1, "https://vinpearl.com/vi/cua-hoi/phong/beach-view-deluxe",             "View biển Cửa Lò, giá tốt nhất hệ thống Vinpearl, bãi biển sát resort"),
            (8, "Ocean Suite Cửa Hội",            2, 1, "Biển",     "Gia đình, Cặp đôi",           "mid",    2800000, 1, "https://vinpearl.com/vi/cua-hoi/phong/ocean-suite",                   "Suite view biển, bãi biển Cửa Lò ngay trước mặt"),
            # VP_HP (resort_id=9)
            (9, "Golf View Deluxe Hải Phòng",    2, 0, "Sân Golf",  "Cặp đôi, Solo",              "mid",    2200000, 1, "https://vinpearl.com/vi/hai-phong/phong/golf-view-deluxe",            "View sân golf, gần bến tàu Cát Bà, kết hợp nghỉ dưỡng và golf"),
            (9, "Ocean Suite Hải Phòng",          2, 1, "Biển",     "Cặp đôi, Gia đình nhỏ",      "luxury", 4500000, 1, "https://vinpearl.com/vi/hai-phong/phong/ocean-suite",                 "Suite view biển, gần sân golf 18 lỗ và bến tàu Cát Bà"),
        ],
    )

    conn.executemany(
        """INSERT INTO vp_promotion
           (destination_id, resort_id, name, discount_type, discount_value,
            valid_from, valid_to, min_nights, conditions, source_url)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        [
            (1, None, "Hè Vàng Phú Quốc 2026",               "percentage",  20.0,    "2026-06-01","2026-08-31", 2, "Giảm 20% khi đặt từ 2 đêm tại bất kỳ resort Vinpearl Phú Quốc mùa hè 2026",        "https://vinpearl.com/vi/khuyen-mai/he-vang-phu-quoc-2026"),
            (None, 5, "Vinpearl Nha Trang — Ưu Đãi Cặp Đôi", "percentage",  15.0,    "2026-05-01","2026-09-30", 2, "Giảm 15% cho cặp đôi từ 2 đêm. Tặng bữa tối lãng mạn 500.000 VND",                 "https://vinpearl.com/vi/khuyen-mai/couple-nha-trang"),
            (None, 4, "Safari Family Package Phú Quốc",       "combo",       25.0,    "2026-01-01","2026-12-31", 2, "Giảm 25% + vé Safari miễn phí cho 2 trẻ em dưới 12 tuổi. Tối thiểu 2 đêm",          "https://vinpearl.com/vi/khuyen-mai/safari-family-package"),
            (None, None,"Early Bird Vinpearl — Đặt Sớm Giảm 10%","percentage",10.0,  "2026-01-01","2026-12-31", 1, "Giảm 10% khi đặt trước ít nhất 10 ngày. Áp dụng toàn hệ thống Vinpearl",            "https://vinpearl.com/vi/khuyen-mai/early-bird"),
            (None, 7, "Hội An Sunset Package",                "free_night",   1.0,    "2026-10-01","2026-12-31", 3, "Ở 3 đêm tặng 1 đêm miễn phí. Bao gồm tour phố cổ Hội An ban đêm miễn phí",          "https://vinpearl.com/vi/khuyen-mai/hoi-an-sunset-package"),
            (None, 6, "Luxury Summer Nha Trang 2026",         "percentage",  20.0,    "2026-07-01","2026-08-31", 2, "Giảm 20% villa & suite. Tặng dịch vụ spa 60 phút/người",                            "https://vinpearl.com/vi/khuyen-mai/luxury-summer-nha-trang"),
            (None, 8, "Cửa Hội Biển Xanh Hè 2026",          "fixed_amount",300000.0, "2026-06-01","2026-08-31", 2, "Giảm 300.000 VND/đêm khi đặt từ 2 đêm. Tặng tour Đảo Ngư miễn phí",                "https://vinpearl.com/vi/khuyen-mai/cua-hoi-bien-xanh"),
            (None, 9, "Vinpearl Golf & Stay Hải Phòng",       "combo",       15.0,    "2026-04-01","2026-11-30", 2, "Giảm 15% + 1 vòng golf 18 lỗ/ngày/khách. Áp dụng Thứ 2-Thứ 6",                    "https://vinpearl.com/vi/khuyen-mai/golf-stay-hai-phong"),
        ],
    )

    conn.commit()
    conn.close()
    print("[DB] Vinpearl data seeded (21 rooms, 8 promotions)")


def _vp_room_match_score(row: Dict, who: str, budget: str, style: str) -> float:
    """Higher score = better fit for who + budget tier + style."""
    price = float(row.get("price_per_night") or 0)
    suitable = (row.get("suitable_for") or "").lower()
    level = (row.get("budget_level") or "mid").lower()
    resort_type = (row.get("resort_type") or "").lower()
    view = (row.get("view_type") or "").lower()

    who_terms = {
        "family": ("gia đình", "trẻ", "family"),
        "couple": ("cặp đôi", "couple"),
        "solo": ("solo",),
        "group": ("nhóm", "group", "bạn"),
    }
    score = 0.0
    for term in who_terms.get(who, ("cặp đôi",)):
        if term in suitable:
            score += 12.0
            break
    else:
        if who == "family" and "gia đình" in suitable:
            score += 12.0
        elif who == "couple" and "cặp" in suitable:
            score += 8.0
        else:
            score += 2.0

    if budget == "thấp":
        if price < 3_000_000:
            score += 20.0 - (price / 3_000_000) * 3.0
        else:
            score -= 30.0
        if level == "mid":
            score += 4.0
    elif budget == "trung":
        if 3_000_000 <= price <= 6_000_000:
            mid = 4_500_000
            score += 18.0 - abs(price - mid) / 1_500_000
        else:
            score -= 25.0
        if level in ("mid",):
            score += 6.0
        elif level == "luxury" and price <= 6_000_000:
            score += 2.0
    else:  # cao — trên 6 triệu/đêm
        if price > 6_000_000:
            score += 18.0 + (price - 6_000_000) / 2_000_000
        elif price > 5_000_000:
            score += 4.0
        else:
            score -= 25.0
        if level in ("luxury", "ultra"):
            score += 8.0

    if style == "biển":
        if "biển" in view or resort_type == "resort":
            score += 5.0
    elif style == "vui chơi":
        if resort_type in ("discovery", "safari", "grand_world"):
            score += 6.0
        else:
            score += 2.0
    else:
        score += 4.0

    if who == "family" and row.get("capacity_children", 0) >= 1:
        score += 5.0

    return score


def get_vp_rooms(destination_id: int, who: str, budget: str, style: str) -> List[Dict]:
    """
    Query rooms from DB matching user preferences.
    Returns list of dicts ordered by match score (best first).
    """
    who_map = {"family": "Gia đình", "couple": "Cặp đôi", "solo": "Solo", "group": "Nhóm"}
    who_kw = who_map.get(who, "Cặp đôi")

    style_clause = ""
    if style == "biển":
        style_clause = "AND (rm.view_type LIKE '%Biển%' OR rs.resort_type = 'resort')"
    elif style == "vui chơi":
        style_clause = "AND rs.resort_type IN ('discovery', 'safari', 'grand_world')"

    sql = f"""
        SELECT rm.id, rm.resort_id, rm.name, rm.capacity_adults, rm.capacity_children,
               rm.view_type, rm.suitable_for, rm.budget_level,
               rm.price_per_night, rm.breakfast_included, rm.source_url, rm.highlights,
               rs.name AS resort_name, rs.resort_type, rs.address
        FROM vp_room rm
        JOIN vp_resort rs ON rm.resort_id = rs.id
        WHERE rs.destination_id = ?
          AND rm.is_active = 1
          AND rs.is_active = 1
          AND rm.suitable_for LIKE ?
          {style_clause}
    """
    def _query(who_pattern: str) -> List[Dict]:
        conn = _sqlite_conn()
        out = [dict(r) for r in conn.execute(sql, (destination_id, who_pattern)).fetchall()]
        conn.close()
        return out

    try:
        rows = _query(f"%{who_kw}%")
        if not rows and who == "family":
            rows = _query("%Gia đình%")
        if not rows:
            rows = _query("%")
        if not rows:
            return []
        rows.sort(
            key=lambda r: _vp_room_match_score(r, who, budget, style),
            reverse=True,
        )
        best = rows[0]
        if not _room_in_budget_tier(float(best.get("price_per_night") or 0), budget):
            in_tier = [r for r in rows if _room_in_budget_tier(float(r.get("price_per_night") or 0), budget)]
            if not in_tier:
                rows = _query("%")
            else:
                in_tier.sort(
                    key=lambda r: _vp_room_match_score(r, who, budget, style),
                    reverse=True,
                )
                rows = in_tier + [r for r in rows if r not in in_tier]
            rows.sort(
                key=lambda r: _vp_room_match_score(r, who, budget, style),
                reverse=True,
            )
        return rows[:5]
    except Exception as e:
        print(f"[DB] get_vp_rooms error: {e}")
        return []


def _room_in_budget_tier(price: float, budget: str) -> bool:
    if budget == "thấp":
        return price < 3_000_000
    if budget == "trung":
        return 3_000_000 <= price <= 6_000_000
    return price > 6_000_000


def get_vp_promotions(destination_id: int, resort_id: int) -> List[Dict]:
    """
    Query active promotions for a resort or destination.
    Checks validity date against today (SQLite date('now')).
    """
    sql = """
        SELECT * FROM vp_promotion
        WHERE is_active = 1
          AND is_verified = 1
          AND date('now') BETWEEN valid_from AND valid_to
          AND (
            resort_id = ?
            OR destination_id = ?
            OR (destination_id IS NULL AND resort_id IS NULL)
          )
        ORDER BY discount_value DESC
        LIMIT 3
    """
    try:
        conn = _sqlite_conn()
        rows = [dict(r) for r in conn.execute(sql, (resort_id, destination_id)).fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] get_vp_promotions error: {e}")
        return []
