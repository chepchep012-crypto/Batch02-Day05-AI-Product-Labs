from __future__ import annotations


def get_destinations() -> str:
    """Return the list of 5 supported Vinpearl destinations."""
    return (
        "VinBot hỗ trợ 5 điểm đến Vinpearl:\n\n"
        "| # | Điểm đến | Từ khoá nhận diện | Nổi bật |\n"
        "|:---:|---|---|---|\n"
        "| 1 | 🏝️ **Phú Quốc** | phú quốc, phu quoc | Đảo ngọc, VinWonders, Safari, resort cao cấp |\n"
        "| 2 | 🌊 **Nha Trang** | nha trang | Biển đẹp, VinWonders, hải sản tươi |\n"
        "| 3 | 🏖️ **Nam Hội An** | **hội an**, hoi an, nam hội an | Vui chơi ven biển, cách phố cổ Hội An 30 phút |\n"
        "| 4 | 🌅 **Cửa Hội** | cửa hội, nghệ an, vinh | Biển yên tĩnh, gần thành phố Vinh |\n"
        "| 5 | ⚓ **Hải Phòng** | hải phòng, cát bà | Đảo Cát Bà, cảng biển, ẩm thực phong phú |\n\n"
        "Bạn muốn đến điểm nào? Gõ tên hoặc số thứ tự."
    )
