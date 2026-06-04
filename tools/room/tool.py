import json
from pathlib import Path

# ── Load data ─────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent.parent / "data" / "vinpearl.json"

with open(DATA_PATH, encoding="utf-8") as f:
    DB = json.load(f)

HOTELS      = DB["hotels"]
DESTINATIONS = DB["destinations"]
REDIRECTS   = DB["redirects"]
LINKS       = DB["links"]
NON_VIN     = DB["non_vinpearl_redirect"]


# ── Helper: resolve alias → destination_id ────────────────────────────────────
def resolve_destination(raw: str) -> str | None:
    """
    Nhận chuỗi người dùng nhập (vd: "phú quốc", "phuquoc", "đảo ngọc")
    Trả về destination_id chuẩn (vd: "phu-quoc") hoặc None nếu không tìm thấy.
    """
    raw = raw.strip().lower()
    for dest_id, dest in DESTINATIONS.items():
        if raw == dest["name"].lower():
            return dest_id
        if raw in [alias.lower() for alias in dest.get("aliases", [])]:
            return dest_id
    return None


# ── Helper: format link object ─────────────────────────────────────────────────
def get_links(keys: list[str]) -> list[dict]:
    return [LINKS[k] for k in keys if k in LINKS]


# ── Helper: filter phòng theo guests + budget + ngày checkin ──────────────────
def filter_rooms(rooms: list[dict], guests: int, max_budget: int | None, checkin_date: str | None = None) -> list[dict]:
    result = []
    for room in rooms:
        if room["status"] != "available":
            continue
        if room["guests"] < guests:
            continue
        if max_budget and room["price_vnd"] > max_budget:
            continue
        if checkin_date and checkin_date in room.get("unavailable_dates", []):
            continue
        result.append(room)
    return result


# ── Main function ──────────────────────────────────────────────────────────────
def run(destination: str, guests: int = 2, max_budget: int | None = None, checkin_date: str | None = None) -> dict:
    """
    Tìm phòng Vinpearl theo địa điểm.

    Args:
        destination:  Tên địa điểm (alias hoặc tên chuẩn)
        guests:       Số khách (mặc định 2)
        max_budget:   Ngân sách tối đa/đêm (VNĐ), None = không giới hạn
        checkin_date: Ngày nhận phòng định dạng YYYY-MM-DD, None = không lọc theo ngày

    Returns:
        dict với status: "found" | "sold_out" | "not_found"
    """

    # Bước 1 — Resolve destination
    dest_id = resolve_destination(destination)

    # Bước 2 — Không tìm thấy destination
    if dest_id is None:
        nearest_info = NON_VIN["known_places"].get(destination.strip().lower())
        nearest_id   = nearest_info["nearest"] if nearest_info else None
        nearest_name = DESTINATIONS[nearest_id]["name"] if nearest_id else None

        return {
            "status": "not_found",
            "destination_input": destination,
            "message": NON_VIN["default"]["message"].replace("{place}", destination),
            "nearest_destination": nearest_name,
            "links": get_links(NON_VIN["default"]["show_links"]),
        }

    dest_name = DESTINATIONS[dest_id]["name"]

    # Bước 3 — Lấy hotels theo destination
    hotels_raw = HOTELS.get(dest_id, [])

    if not hotels_raw:
        return {
            "status": "not_found",
            "destination_id": dest_id,
            "destination_name": dest_name,
            "message": f"Vinpearl chưa có cơ sở tại {dest_name}.",
            "links": get_links(["all_hotels"]),
        }

    # Bước 4 — Filter phòng available theo guests + budget
    hotels_result = []
    for hotel in hotels_raw:
        available_rooms = filter_rooms(hotel["rooms"], guests, max_budget, checkin_date)
        if available_rooms:
            hotels_result.append({
                "id":          hotel["id"],
                "name":        hotel["name"],
                "star":        hotel["star"],
                "area":        hotel["area"],
                "phone":       hotel["phone"],
                "booking_url": hotel["booking_url"],
                "source":      hotel["source"],
                "rooms":       available_rooms,
            })

    # Bước 5 — Không còn phòng nào
    if not hotels_result:
        redirect = REDIRECTS["no_room"]
        return {
            "status": "sold_out",
            "destination_id": dest_id,
            "destination_name": dest_name,
            "message": redirect["message"].replace("{hotel}", dest_name),
            "links": get_links(redirect["show_links"]),
        }

    # Bước 6 — Có phòng → trả kết quả
    return {
        "status": "found",
        "destination_id": dest_id,
        "destination_name": dest_name,
        "guests": guests,
        "max_budget": max_budget,
        "hotels": hotels_result,
        "links": get_links(["booking_home", "hotline"]),
    }


# ── Quick test khi chạy trực tiếp ─────────────────────────────────────────────
if __name__ == "__main__":
    test_cases = [
        # Happy case
        {"destination": "phú quốc", "guests": 2},
        # Filter theo budget
        {"destination": "nha trang", "guests": 2, "max_budget": 4000000},
        # Sold out (tất cả sold_out sau filter)
        {"destination": "nha trang", "guests": 2, "max_budget": 1000000},
        # Not found — alias địa phương
        {"destination": "đà lạt"},
        # Not found — ngoài VN
        {"destination": "bangkok"},
        # Filter theo ngày — Deluxe Phú Quốc hết ngày 06/06
        {"destination": "phú quốc", "guests": 2, "checkin_date": "2026-06-06"},
        # Filter theo ngày — Phú Quốc ngày 05/06 còn đủ phòng
        {"destination": "phú quốc", "guests": 2, "checkin_date": "2026-06-05"},
    ]

    for tc in test_cases:
        result = run(**tc)
        print(f"\n{'='*55}")
        print(f"Input : {tc}")
        print(f"Status: {result['status']}")
        if result["status"] == "found":
            for h in result["hotels"]:
                print(f"  🏨 {h['name']} ({h['star']}⭐)")
                for r in h["rooms"]:
                    print(f"     - {r['type']} | {r['guests']} khách | {r['price_vnd']:,} VNĐ")
        else:
            print(f"  💬 {result['message']}")
            if result.get("nearest_destination"):
                print(f"  📍 Gợi ý gần nhất: {result['nearest_destination']}")