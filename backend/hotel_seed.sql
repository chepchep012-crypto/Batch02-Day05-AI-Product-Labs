-- ============================================================
--  MOCK DATA - HOTEL MANAGEMENT SYSTEM
--  Phiên bản: 1.0
--  Ngày tạo: 2026-06-04
--  Thứ tự insert: tuân theo ràng buộc khóa ngoại
-- ============================================================



-- ============================================================
-- 1. ROOM_TYPE (5 loại phòng)
-- ============================================================
INSERT INTO room_type (type_name, base_price, capacity, num_beds, bed_type, area_sqm, floor_type, description, thumbnail_url, is_active) VALUES
('Standard',          1200000.00, 2, 1, 'Queen', 25.00, 'Thảm', 'Phòng tiêu chuẩn với đầy đủ tiện nghi cơ bản, view thành phố thoáng đãng.', 'https://hotel.example.com/rooms/standard.jpg', 1),
('Deluxe',            1800000.00, 2, 1, 'King',  35.00, 'Gỗ',   'Phòng Deluxe rộng rãi với giường King size, ban công và view biển hoặc sân vườn.', 'https://hotel.example.com/rooms/deluxe.jpg', 1),
('Junior Suite',      2500000.00, 3, 1, 'King',  50.00, 'Gỗ',   'Phòng Junior Suite với phòng khách nhỏ, bồn tắm riêng và view tuyệt vời.', 'https://hotel.example.com/rooms/junior-suite.jpg', 1),
('Senior Suite',      3500000.00, 4, 2, 'King',  75.00, 'Đá',   'Phòng Senior Suite sang trọng với 2 phòng ngủ, phòng khách rộng và bồn tắm Jacuzzi.', 'https://hotel.example.com/rooms/senior-suite.jpg', 1),
('Presidential Suite',8000000.00, 6, 2, 'King', 120.00, 'Đá',   'Phòng Presidential Suite đẳng cấp nhất với 3 phòng ngủ, hồ bơi riêng và butler 24/7.', 'https://hotel.example.com/rooms/presidential.jpg', 1);

-- ============================================================
-- 2. ROOM_TYPE_AMENITY
-- ============================================================
INSERT INTO room_type_amenity (room_type_id, amenity_name, amenity_icon) VALUES
-- Standard (room_type_id=1)
(1, 'WiFi miễn phí',              'fa-wifi'),
(1, 'TV màn hình phẳng',          'fa-tv'),
(1, 'Điều hòa',                   'fa-snowflake'),
(1, 'Két an toàn',                'fa-lock'),
(1, 'Minibar',                    'fa-wine-bottle'),
-- Deluxe (room_type_id=2)
(2, 'WiFi miễn phí',              'fa-wifi'),
(2, 'TV màn hình phẳng 55"',      'fa-tv'),
(2, 'Điều hòa',                   'fa-snowflake'),
(2, 'Két an toàn',                'fa-lock'),
(2, 'Minibar cao cấp',            'fa-wine-bottle'),
(2, 'Ban công riêng',             'fa-door-open'),
(2, 'Bồn tắm',                    'fa-bath'),
-- Junior Suite (room_type_id=3)
(3, 'WiFi tốc độ cao',            'fa-wifi'),
(3, 'TV màn hình phẳng 65"',      'fa-tv'),
(3, 'Điều hòa 2 chiều',           'fa-snowflake'),
(3, 'Két an toàn',                'fa-lock'),
(3, 'Minibar cao cấp',            'fa-wine-bottle'),
(3, 'Bồn tắm Jacuzzi',            'fa-hot-tub'),
(3, 'Phòng khách nhỏ',            'fa-couch'),
(3, 'Máy pha cà phê Nespresso',   'fa-coffee'),
-- Senior Suite (room_type_id=4)
(4, 'WiFi tốc độ cao',            'fa-wifi'),
(4, 'Smart TV 75"',               'fa-tv'),
(4, 'Điều hòa thông minh',        'fa-snowflake'),
(4, 'Két an toàn',                'fa-lock'),
(4, 'Minibar Premium',            'fa-wine-bottle'),
(4, 'Bồn tắm Jacuzzi',            'fa-hot-tub'),
(4, 'Phòng khách rộng',           'fa-couch'),
(4, 'Máy pha cà phê Nespresso',   'fa-coffee'),
(4, 'Butler riêng (7h–22h)',       'fa-concierge-bell'),
-- Presidential Suite (room_type_id=5)
(5, 'WiFi tốc độ cực cao',        'fa-wifi'),
(5, 'Smart TV 85" + Bose Sound',  'fa-tv'),
(5, 'Điều hòa thông minh',        'fa-snowflake'),
(5, 'Két an toàn cao cấp',        'fa-lock'),
(5, 'Bar mini đầy đủ',            'fa-wine-bottle'),
(5, 'Hồ bơi riêng',              'fa-swimming-pool'),
(5, 'Bồn tắm Jacuzzi',            'fa-hot-tub'),
(5, 'Phòng khách + Phòng ăn',     'fa-couch'),
(5, 'Espresso Bar Nespresso',      'fa-coffee'),
(5, 'Butler riêng 24/7',          'fa-concierge-bell'),
(5, 'Xe đón sân bay miễn phí',    'fa-car');

-- ============================================================
-- 3. DEPARTMENT (chưa có manager_id — thêm sau khi có Staff)
-- ============================================================
INSERT INTO department (dept_name, dept_code, description, is_active) VALUES
('Front Office',  'FO', 'Bộ phận lễ tân, đặt phòng và quan hệ khách hàng', 1),
('Housekeeping',  'HK', 'Bộ phận buồng phòng và vệ sinh',                  1),
('Food & Beverage','FB','Bộ phận ẩm thực và đồ uống',                      1),
('Maintenance',   'MT', 'Bộ phận kỹ thuật và bảo trì',                    1),
('Administration','AD', 'Bộ phận hành chính và quản lý',                   1);

-- ============================================================
-- 4. STAFF (12 nhân viên)
-- ============================================================
INSERT INTO staff (employee_code, full_name, email, phone, department_id, role, shift, hire_date, salary, is_active) VALUES
('EMP-001', 'Nguyễn Văn An',   'an.nguyen@hotel.com',   '0901234001', 1, 'Front Office Manager',   'morning',   '2020-01-15', 25000000.00, 1),
('EMP-002', 'Trần Thị Bình',   'binh.tran@hotel.com',   '0901234002', 1, 'Receptionist',           'morning',   '2021-03-01', 12000000.00, 1),
('EMP-003', 'Lê Văn Cường',    'cuong.le@hotel.com',    '0901234003', 1, 'Receptionist',           'afternoon', '2021-06-15', 12000000.00, 1),
('EMP-004', 'Phạm Thị Dung',   'dung.pham@hotel.com',   '0901234004', 2, 'Housekeeping Manager',   'morning',   '2019-08-01', 22000000.00, 1),
('EMP-005', 'Hoàng Văn Em',    'em.hoang@hotel.com',    '0901234005', 2, 'Housekeeper',            'morning',   '2022-01-10',  9000000.00, 1),
('EMP-006', 'Võ Thị Phương',   'phuong.vo@hotel.com',   '0901234006', 2, 'Housekeeper',            'afternoon', '2022-04-01',  9000000.00, 1),
('EMP-007', 'Đặng Văn Giang',  'giang.dang@hotel.com',  '0901234007', 3, 'F&B Manager',            'morning',   '2020-05-20', 23000000.00, 1),
('EMP-008', 'Bùi Thị Hương',   'huong.bui@hotel.com',   '0901234008', 3, 'Waiter',                 'morning',   '2023-02-01',  8500000.00, 1),
('EMP-009', 'Trịnh Văn Ích',   'ich.trinh@hotel.com',   '0901234009', 4, 'Maintenance Engineer',   'morning',   '2021-09-15', 13000000.00, 1),
('EMP-010', 'Ngô Thị Kim',     'kim.ngo@hotel.com',     '0901234010', 5, 'General Manager',        'flexible',  '2018-03-01', 45000000.00, 1),
('EMP-011', 'Đinh Văn Long',   'long.dinh@hotel.com',   '0901234011', 4, 'Maintenance Technician', 'afternoon', '2023-07-01', 11000000.00, 1),
('EMP-012', 'Lý Thị Mai',      'mai.ly@hotel.com',      '0901234012', 1, 'Night Auditor',          'night',     '2022-11-01', 13500000.00, 1);

-- Gán manager cho từng phòng ban
UPDATE department SET manager_id = 1  WHERE department_id = 1;  -- FO: Nguyễn Văn An
UPDATE department SET manager_id = 4  WHERE department_id = 2;  -- HK: Phạm Thị Dung
UPDATE department SET manager_id = 7  WHERE department_id = 3;  -- FB: Đặng Văn Giang
UPDATE department SET manager_id = 9  WHERE department_id = 4;  -- MT: Trịnh Văn Ích
UPDATE department SET manager_id = 10 WHERE department_id = 5;  -- AD: Ngô Thị Kim

-- ============================================================
-- 5. STAFF_ACCOUNT
-- ============================================================
INSERT INTO staff_account (staff_id, username, password_hash, role_level, is_active) VALUES
(1,  'an.nguyen',    '$2b$12$hashed_password_an',    'manager',    1),
(2,  'binh.tran',    '$2b$12$hashed_password_binh',  'staff',      1),
(3,  'cuong.le',     '$2b$12$hashed_password_cuong', 'staff',      1),
(4,  'dung.pham',    '$2b$12$hashed_password_dung',  'manager',    1),
(7,  'giang.dang',   '$2b$12$hashed_password_giang', 'manager',    1),
(10, 'kim.ngo',      '$2b$12$hashed_password_kim',   'admin',      1),
(12, 'mai.ly',       '$2b$12$hashed_password_mai',   'staff',      1);

-- ============================================================
-- 6. SHIFT_SCHEDULE (lịch ca 2-4/06/2026)
-- ============================================================
INSERT INTO shift_schedule (staff_id, shift_date, shift_type, start_time, end_time, actual_start, actual_end, notes) VALUES
(1,  '2026-06-02', 'morning',   '08:00:00', '16:00:00', '07:55:00', '16:05:00', NULL),
(2,  '2026-06-02', 'morning',   '07:00:00', '15:00:00', '07:00:00', '15:00:00', NULL),
(3,  '2026-06-02', 'afternoon', '15:00:00', '23:00:00', '15:10:00', '23:05:00', NULL),
(4,  '2026-06-02', 'morning',   '08:00:00', '16:00:00', '07:50:00', '16:15:00', NULL),
(5,  '2026-06-02', 'morning',   '08:00:00', '16:00:00', '08:00:00', '16:00:00', NULL),
(6,  '2026-06-02', 'afternoon', '14:00:00', '22:00:00', '14:00:00', '22:00:00', NULL),
(12, '2026-06-02', 'night',     '23:00:00', '07:00:00', '23:00:00', '07:00:00', NULL),
(1,  '2026-06-03', 'morning',   '08:00:00', '16:00:00', '08:00:00', '16:00:00', NULL),
(2,  '2026-06-03', 'morning',   '07:00:00', '15:00:00', '07:05:00', '15:00:00', NULL),
(3,  '2026-06-03', 'afternoon', '15:00:00', '23:00:00', '15:00:00', '23:00:00', NULL),
(5,  '2026-06-03', 'morning',   '08:00:00', '16:00:00', '08:00:00', '16:00:00', NULL),
(6,  '2026-06-03', 'afternoon', '14:00:00', '22:00:00', '14:00:00', '22:00:00', NULL),
(1,  '2026-06-04', 'morning',   '08:00:00', '16:00:00', '07:58:00', NULL,        NULL),
(2,  '2026-06-04', 'morning',   '07:00:00', '15:00:00', '07:00:00', NULL,        NULL),
(4,  '2026-06-04', 'morning',   '08:00:00', '16:00:00', '08:00:00', NULL,        NULL),
(5,  '2026-06-04', 'morning',   '08:00:00', '16:00:00', '08:00:00', NULL,        NULL),
(6,  '2026-06-04', 'afternoon', '14:00:00', '22:00:00', NULL,        NULL,        NULL),
(9,  '2026-06-04', 'morning',   '08:00:00', '16:00:00', '08:10:00', NULL,        'Ưu tiên sửa điều hòa phòng 102');

-- ============================================================
-- 7. ROOM_TYPE_PROMOTION (7 ưu đãi)
-- ============================================================
INSERT INTO room_type_promotion (room_type_id, promotion_name, discount_type, discount_value, min_nights, valid_from, valid_to, day_of_week, max_uses, used_count, conditions, is_active, created_by) VALUES
(1, 'Early Bird 7 ngày',   'percentage',    15.00, 2, '2026-01-01', '2026-12-31', 'All',     NULL, 45, 'Đặt trước ít nhất 7 ngày để được giảm 15%',                                    1, 1),
(2, 'Weekend Getaway',     'percentage',    10.00, 2, '2026-01-01', '2026-12-31', 'Weekend', 100,  28, 'Áp dụng cuối tuần (Thứ 6–CN) từ 2 đêm trở lên',                               1, 1),
(3, 'Tuần Trăng Mật',      'percentage',    20.00, 3, '2026-01-01', '2026-12-31', 'All',     50,   12, 'Ưu đãi cặp đôi tuần trăng mật. Tặng kèm hoa tươi và bánh ngọt chào mừng',     1, 1),
(4, 'Summer Special',      'fixed_amount', 500000.00, 2, '2026-06-01', '2026-08-31', 'All',  30,    5, 'Giảm 500.000 VND/đêm cho mùa hè 2026',                                        1, 1),
(5, 'VIP Long Stay',       'percentage',    25.00, 7, '2026-01-01', '2026-12-31', 'All',     10,    2, 'Ưu đãi khách lưu trú dài hạn từ 7 đêm tại Presidential Suite',                 1, 10),
(1, 'Khuyến Mãi Tết 2027', 'percentage',     5.00, 1, '2027-01-20', '2027-02-05', 'All',    200,   0, 'Ưu đãi mùa Tết Nguyên Đán 2027',                                              1, 10),
(2, 'Flash Sale Hè',       'percentage',    30.00, 1, '2026-06-15', '2026-06-30', 'All',     20,    3, 'Flash sale cuối tháng 6 — số lượng có hạn!',                                  1, 10);

-- ============================================================
-- 8. ROOM (15 phòng)
-- ============================================================
INSERT INTO room (room_number, floor, room_type_id, view_type, status, last_cleaned_at, notes, is_active) VALUES
('101',  1, 1, 'Garden', 'available',    '2026-06-04 08:00:00', NULL,                                     1),
('102',  1, 1, 'City',   'maintenance',  '2026-06-03 09:00:00', 'Đang sửa điều hòa — dự kiến xong 5/6',  1),
('103',  1, 1, 'City',   'available',    '2026-06-04 08:30:00', NULL,                                     1),
('201',  2, 2, 'Sea',    'occupied',     '2026-06-02 10:00:00', NULL,                                     1),
('202',  2, 2, 'Sea',    'available',    '2026-06-04 09:00:00', NULL,                                     1),
('203',  2, 2, 'Garden', 'cleaning',     '2026-06-04 07:00:00', 'Đang dọn sau checkout sáng nay',         1),
('204',  2, 2, 'City',   'available',    '2026-06-04 08:45:00', NULL,                                     1),
('301',  3, 3, 'Sea',    'occupied',     '2026-06-01 11:00:00', NULL,                                     1),
('302',  3, 3, 'Sea',    'available',    '2026-06-04 09:30:00', NULL,                                     1),
('303',  3, 3, 'Pool',   'available',    '2026-06-04 09:00:00', NULL,                                     1),
('401',  4, 4, 'Sea',    'occupied',     '2026-06-03 12:00:00', NULL,                                     1),
('402',  4, 4, 'Sea',    'available',    '2026-06-04 10:00:00', NULL,                                     1),
('403',  4, 4, 'Pool',   'available',    '2026-06-04 10:00:00', NULL,                                     1),
('PH01', 5, 5, 'Sea',    'occupied',     '2026-06-02 14:00:00', 'Phòng VIP — butler đang trực',           1),
('PH02', 5, 5, 'City',   'available',    '2026-06-04 10:30:00', NULL,                                     1);

-- ============================================================
-- 9. ROOM_RATE (giá theo mùa / thứ trong tuần)
-- ============================================================
INSERT INTO room_rate (room_type_id, rate_name, price, valid_from, valid_to, day_of_week, priority) VALUES
(1, 'Cuối tuần Standard',       1400000.00, '2026-01-01', '2026-12-31', 'Weekend', 1),
(2, 'Cuối tuần Deluxe',         2100000.00, '2026-01-01', '2026-12-31', 'Weekend', 1),
(3, 'Cuối tuần Junior Suite',   2900000.00, '2026-01-01', '2026-12-31', 'Weekend', 1),
(4, 'Cuối tuần Senior Suite',   4000000.00, '2026-01-01', '2026-12-31', 'Weekend', 1),
(5, 'Cuối tuần Presidential',   9000000.00, '2026-01-01', '2026-12-31', 'Weekend', 1),
(1, 'Mùa hè Standard',          1350000.00, '2026-06-01', '2026-08-31', 'All',     2),
(2, 'Mùa hè Deluxe',            2000000.00, '2026-06-01', '2026-08-31', 'All',     2),
(3, 'Mùa hè Junior Suite',      2800000.00, '2026-06-01', '2026-08-31', 'All',     2),
(4, 'Mùa hè Senior Suite',      3800000.00, '2026-06-01', '2026-08-31', 'All',     2),
(5, 'Mùa hè Presidential',      8500000.00, '2026-06-01', '2026-08-31', 'All',     2),
(1, 'Tết Nguyên Đán 2027',      2400000.00, '2027-01-20', '2027-02-05', 'All',     5),
(2, 'Tết Nguyên Đán 2027',      3600000.00, '2027-01-20', '2027-02-05', 'All',     5),
(3, 'Tết Nguyên Đán 2027',      5000000.00, '2027-01-20', '2027-02-05', 'All',     5);

-- ============================================================
-- 10. GUEST (10 khách)
-- ============================================================
INSERT INTO guest (full_name, email, phone, id_number, id_type, id_issue_date, id_expiry_date, nationality, date_of_birth, gender, address, city, country, company_name, loyalty_tier, loyalty_points, total_stays, total_spent, preferred_room_type, special_notes, is_blacklisted) VALUES
('Nguyễn Hoàng Minh', 'minh.nguyen@gmail.com',    '0912345001', '079123456789', 'CCCD',     '2020-05-10', '2030-05-10', 'Vietnamese', '1988-03-15', 'Male',   '123 Lê Lợi, Q.1',             'TP.HCM',   'Vietnam',       NULL,                   'Gold',     2500, 8,  45000000.00, 2, 'Thích phòng view biển, không hút thuốc',                             0),
('Trần Thanh Hà',     'ha.tran@yahoo.com',         '0912345002', '048234567890', 'CCCD',     '2021-07-20', '2031-07-20', 'Vietnamese', '1992-11-22', 'Female', '456 Trần Hưng Đạo, Q.5',     'TP.HCM',   'Vietnam',       'Công ty ABC',          'Silver',    800, 3,  15000000.00, 1, 'Dị ứng hải sản — cần giường đơn',                                    0),
('Lê Đức Anh',        'duc.anh@hotmail.com',       '0912345003', '001345678901', 'CCCD',     '2019-12-01', '2029-12-01', 'Vietnamese', '1975-07-08', 'Male',   '789 Hùng Vương, Ba Đình',    'Hà Nội',   'Vietnam',       'Tập đoàn XYZ',         'Platinum', 8500, 25, 280000000.00, 4, 'Khách VIP, thích rượu vang đỏ. Butler thông báo trước 30 phút',     0),
('Phạm Thị Lan',      'lan.pham@gmail.com',        '0912345004', '036456789012', 'CCCD',     '2022-03-15', '2032-03-15', 'Vietnamese', '1995-04-30', 'Female', '321 Nguyễn Huệ, Hải Châu',   'Đà Nẵng',  'Vietnam',       NULL,                   'Standard',  150, 1,   3600000.00, 1, NULL,                                                                  0),
('John Smith',        'john.smith@email.com',      '+15550101',  'US123456789',  'Passport', '2020-06-15', '2030-06-15', 'American',   '1980-09-12', 'Male',   '123 Main St, New York',      'New York', 'United States', 'Smith & Associates',   'Gold',     3200, 10, 120000000.00, 3, 'Cần gối mềm, ăn chay',                                               0),
('Yamamoto Kenji',    'kenji.yamamoto@jp.com',     '+819012345678','JP987654321','Passport', '2021-04-01', '2031-04-01', 'Japanese',   '1985-12-25', 'Male',   '5-10-15 Shinjuku, Tokyo',    'Tokyo',    'Japan',         'Yamamoto Corp',        'Silver',   1200, 4,  35000000.00, 2, 'Thích phòng yên tĩnh, không muốn bị làm phiền buổi sáng sớm',      0),
('Kim Ji-Young',      'jiyoung.kim@korea.com',     '+821012345678','KR456789012','Passport', '2022-08-10', '2032-08-10', 'Korean',     '1993-02-14', 'Female', '123 Gangnam-gu, Seoul',      'Seoul',    'South Korea',   NULL,                   'Standard',    0, 1,   2500000.00, 2, 'Tuần trăng mật — cần trang trí phòng hoa hồng',                     0),
('Nguyễn Văn Bá',     'ba.nguyen@email.com',       '0912345007', '060567890123', 'CCCD',     '2023-01-20', '2033-01-20', 'Vietnamese', '2000-08-18', 'Male',   '654 Cách Mạng T8, Q.10',     'TP.HCM',   'Vietnam',       NULL,                   'Standard',   50, 2,   5400000.00, 1, NULL,                                                                  0),
('Sophie Dubois',     'sophie.dubois@france.fr',   '+33612345678','FR789012345', 'Passport', '2019-11-05', '2029-11-05', 'French',     '1987-06-20', 'Female', '12 Rue de la Paix, Paris',   'Paris',    'France',        'Dubois International', 'Gold',     2800, 7,  85000000.00, 3, 'Thích rượu vang Pháp, cần ấm nước trong phòng',                     0),
('Hoàng Thị Cẩm',    'cam.hoang@gmail.com',       '0912345009', '027678901234', 'CCCD',     '2020-09-30', '2030-09-30', 'Vietnamese', '1990-12-05', 'Female', '111 Lê Duẩn, Hải Châu',     'Đà Nẵng',  'Vietnam',       'ABC Tours',            'Standard',  200, 3,  12000000.00, 1, 'Đặt phòng cho đoàn khách',                                           0);

-- ============================================================
-- 11. GUEST_ACCOUNT
-- ============================================================
INSERT INTO guest_account (guest_id, username, password_hash, is_active) VALUES
(1, 'minh.nguyen',    '$2b$12$hashed_guest_1', 1),
(2, 'ha.tran',        '$2b$12$hashed_guest_2', 1),
(3, 'duc.anh',        '$2b$12$hashed_guest_3', 1),
(5, 'john.smith',     '$2b$12$hashed_guest_5', 1),
(6, 'kenji.yamamoto', '$2b$12$hashed_guest_6', 1),
(9, 'sophie.dubois',  '$2b$12$hashed_guest_9', 1);

-- ============================================================
-- 12. RESERVATION (11 đặt phòng: đã checkout, đang ở, tương lai, đã hủy)
-- ============================================================

-- --- Đặt phòng đã CHECKOUT (lịch sử) ---
INSERT INTO reservation (reservation_code, guest_id, room_id, promotion_id, check_in_date, check_out_date, num_adults, num_children, room_rate, subtotal, discount_amount, total_amount, deposit_amount, balance_due, source, status, special_requests, confirmed_by) VALUES
-- room_id=4 (201-Deluxe-Sea), promotion_id=2 (Weekend 10%)
('RES-20260520-001', 1, 4, 2, '2026-05-20', '2026-05-23', 2, 0,
 2100000.00, 6300000.00, 630000.00, 5670000.00, 2000000.00, 0.00,
 'website', 'checked_out', 'Cần phòng view biển, tầng cao', 1),
-- room_id=8 (301-Junior Suite-Sea), no promotion
('RES-20260525-002', 5, 8, NULL, '2026-05-25', '2026-05-30', 2, 1,
 2500000.00, 12500000.00, 0.00, 12500000.00, 5000000.00, 0.00,
 'booking_com', 'checked_out', 'Cần giường phụ cho trẻ em', 2),
-- room_id=11 (401-Senior Suite-Sea), promotion_id=4 (Summer Special -500k/đêm)
('RES-20260601-003', 3, 11, 4, '2026-06-01', '2026-06-04', 2, 0,
 3800000.00, 11400000.00, 1500000.00, 9900000.00, 5000000.00, 0.00,
 'phone', 'checked_out', 'Khách VIP — chuẩn bị rượu vang đỏ, butler sẵn sàng', 1);

-- --- Đặt phòng đang CHECKED_IN (hôm nay) ---
INSERT INTO reservation (reservation_code, guest_id, room_id, promotion_id, check_in_date, check_out_date, num_adults, num_children, room_rate, subtotal, discount_amount, total_amount, deposit_amount, balance_due, source, status, special_requests, confirmed_by) VALUES
-- room_id=4 (201-Deluxe-Sea), no promo, Nguyễn Hoàng Minh
('RES-20260602-004', 1, 4, NULL, '2026-06-02', '2026-06-07', 2, 0,
 2000000.00, 10000000.00, 0.00, 10000000.00, 3000000.00, 7000000.00,
 'website', 'checked_in', 'Champagne chào mừng, phòng view biển', 2),
-- room_id=8 (301-Junior Suite-Sea), promotion_id=3 (Honeymoon 20%), Yamamoto Kenji + Kim Ji-Young
('RES-20260603-005', 6, 8, 3, '2026-06-03', '2026-06-07', 2, 0,
 2800000.00, 11200000.00, 2240000.00, 8960000.00, 4000000.00, 4960000.00,
 'agoda', 'checked_in', 'Tuần trăng mật — trang trí phòng hoa hồng đỏ', 2),
-- room_id=14 (PH01-Presidential-Sea), promotion_id=5 (VIP 25%), Lê Đức Anh
('RES-20260604-006', 3, 14, 5, '2026-06-04', '2026-06-11', 1, 0,
 8500000.00, 59500000.00, 14875000.00, 44625000.00, 20000000.00, 24625000.00,
 'phone', 'checked_in', 'Presidential Suite — butler trực 24/7', 1);

-- --- Đặt phòng TƯƠNG LAI (confirmed / pending) ---
INSERT INTO reservation (reservation_code, guest_id, room_id, promotion_id, check_in_date, check_out_date, num_adults, num_children, room_rate, subtotal, discount_amount, total_amount, deposit_amount, balance_due, source, status, special_requests, confirmed_by) VALUES
-- room_id=9 (302-Junior Suite-Sea), Sophie Dubois
('RES-20260608-007', 9, 9, NULL, '2026-06-08', '2026-06-12', 2, 0,
 2500000.00, 10000000.00, 0.00, 10000000.00, 4000000.00, 6000000.00,
 'website', 'confirmed', 'Cần ấm nước và cà phê Pháp trong phòng', 2),
-- room_id=1 (101-Standard-Garden), promotion_id=1 (Early Bird 15%), Phạm Thị Lan
('RES-20260610-008', 4, 1, 1, '2026-06-10', '2026-06-12', 2, 1,
 1350000.00, 2700000.00, 405000.00, 2295000.00, 1000000.00, 1295000.00,
 'website', 'confirmed', 'Lần đầu lưu trú, cần hướng dẫn tiện ích', 2),
-- room_id=3 (103-Standard-City), Trần Thanh Hà, chưa xác nhận
('RES-20260615-009', 2, 3, NULL, '2026-06-15', '2026-06-17', 1, 0,
 1350000.00, 2700000.00, 0.00, 2700000.00, 0.00, 2700000.00,
 'phone', 'pending', 'Cần giường đơn, tránh hải sản trong bữa sáng', NULL),
-- room_id=5 (202-Deluxe-Sea), Hoàng Thị Cẩm (đoàn tour)
('RES-20260620-010', 10, 5, NULL, '2026-06-20', '2026-06-22', 2, 0,
 2000000.00, 4000000.00, 0.00, 4000000.00, 2000000.00, 2000000.00,
 'travel_agent', 'confirmed', 'Đoàn khách du lịch — cần hỗ trợ thêm', 1);

-- --- Đặt phòng đã HỦY ---
INSERT INTO reservation (reservation_code, guest_id, room_id, promotion_id, check_in_date, check_out_date, num_adults, num_children, room_rate, subtotal, discount_amount, total_amount, deposit_amount, balance_due, source, status, cancelled_at, cancel_reason, confirmed_by) VALUES
-- room_id=2 (102-Standard-City), Nguyễn Văn Bá
('RES-20260525-011', 8, 2, NULL, '2026-06-05', '2026-06-07', 2, 0,
 1350000.00, 2700000.00, 0.00, 2700000.00, 1000000.00, 0.00,
 'website', 'cancelled', '2026-05-28 10:30:00', 'Khách đổi lịch công tác đột xuất', 2);

-- ============================================================
-- 13. RESERVATION_GUEST (khách phụ trong đặt phòng)
-- ============================================================
INSERT INTO reservation_guest (reservation_id, full_name, id_number, date_of_birth, nationality, is_primary) VALUES
(1,  'Nguyễn Hoàng Minh', '079123456789', '1988-03-15', 'Vietnamese', 1),
(1,  'Nguyễn Thị Thu',    '079987654321', '1990-06-20', 'Vietnamese', 0),
(2,  'John Smith',         'US123456789',  '1980-09-12', 'American',   1),
(2,  'Emily Smith',        'US123456790',  '1982-04-05', 'American',   0),
(2,  'Tommy Smith',        'US123456791',  '2018-07-15', 'American',   0),
(3,  'Lê Đức Anh',         '001345678901', '1975-07-08', 'Vietnamese', 1),
(4,  'Nguyễn Hoàng Minh', '079123456789', '1988-03-15', 'Vietnamese', 1),
(4,  'Nguyễn Thị Thu',    '079987654321', '1990-06-20', 'Vietnamese', 0),
(5,  'Yamamoto Kenji',     'JP987654321',  '1985-12-25', 'Japanese',   1),
(5,  'Kim Ji-Young',       'KR456789012',  '1993-02-14', 'Korean',     0),
(6,  'Lê Đức Anh',         '001345678901', '1975-07-08', 'Vietnamese', 1),
(7,  'Sophie Dubois',      'FR789012345',  '1987-06-20', 'French',     1),
(8,  'Phạm Thị Lan',       '036456789012', '1995-04-30', 'Vietnamese', 1),
(9,  'Trần Thanh Hà',      '048234567890', '1992-11-22', 'Vietnamese', 1),
(10, 'Hoàng Thị Cẩm',     '027678901234', '1990-12-05', 'Vietnamese', 1);

-- ============================================================
-- 14. CHECK_IN_OUT
-- ============================================================
INSERT INTO check_in_out (reservation_id, actual_check_in, actual_check_out, check_in_by, check_out_by, check_in_notes, check_out_notes, room_condition, damage_description, damage_charge) VALUES
(1, '2026-05-20 14:30:00', '2026-05-23 11:15:00', 2, 3, 'Khách đến đúng giờ, đã nâng cấp view biển', 'Phòng gọn gàng, khách hài lòng', 'good', NULL, 0.00),
(2, '2026-05-25 15:00:00', '2026-05-30 10:45:00', 2, 2, 'Gia đình 3 người, đã bố trí crib cho bé', 'Phòng sạch sẽ, không hư hỏng', 'good', NULL, 0.00),
(3, '2026-06-01 13:00:00', '2026-06-04 10:00:00', 1, 2, 'Khách VIP Lê Đức Anh — rượu vang đỏ đã chuẩn bị', 'Phòng gọn gàng; 1 ly thủy tinh bị vỡ', 'minor_damage', '1 ly thủy tinh vỡ trên bàn làm việc', 150000.00),
(4, '2026-06-02 14:15:00', NULL, 2, NULL, 'Nhận phòng sớm 45 phút, đã thu phí early check-in', NULL, 'good', NULL, 0.00),
(5, '2026-06-03 15:30:00', NULL, 3, NULL, 'Cặp đôi tuần trăng mật — phòng đã trang trí hoa hồng', NULL, 'good', NULL, 0.00),
(6, '2026-06-04 12:00:00', NULL, 1, NULL, 'Khách VIP Lê Đức Anh — Presidential Suite, butler đã sẵn sàng', NULL, 'good', NULL, 0.00);

-- ============================================================
-- 15. SERVICE (18 dịch vụ)
-- ============================================================
INSERT INTO service (service_name, category, unit_price, unit, description, is_available) VALUES
('Bữa sáng buffet',              'F&B',      250000.00,  'người', 'Buffet sáng hơn 50 món từ 06:30–10:00',                         1),
('Bữa tối à la carte',           'F&B',      500000.00,  'người', 'Thực đơn à la carte tại nhà hàng The Pearl',                    1),
('Cocktail / Mocktail',          'F&B',      120000.00,  'ly',    'Đồ uống tại bar Sky Lounge',                                    1),
('Rượu vang (nhà hàng)',         'F&B',      800000.00,  'chai',  'Rượu vang cao cấp tại nhà hàng',                                1),
('Giặt đồ tiêu chuẩn',          'Laundry',   50000.00,  'món',   'Giặt ủi tiêu chuẩn — trả trong 24h',                            1),
('Giặt nhanh',                   'Laundry',   80000.00,  'món',   'Giặt ủi nhanh — trả trong 4h',                                  1),
('Massage thư giãn 60 phút',     'Spa',      600000.00,  'lần',   'Massage thư giãn toàn thân tại Spa by the Sea',                  1),
('Massage đá nóng 90 phút',      'Spa',      900000.00,  'lần',   'Massage đá nóng cao cấp tại Spa',                               1),
('Xe đón / đưa sân bay',         'Transport',350000.00,  'lần',   'Xe 7 chỗ đưa đón sân bay Đà Nẵng',                             1),
('Thuê xe tham quan (có tài)',   'Transport',1200000.00, 'ngày',  'Xe có tài xế tham quan 8 tiếng',                                1),
('Early Check-in (trước 12h)',   'Extra',    200000.00,  'lần',   'Phí nhận phòng trước 12:00',                                   1),
('Late Check-out (sau 12h)',      'Extra',    200000.00,  'lần',   'Phí trả phòng sau 12:00',                                      1),
('Crib (giường em bé)',           'Extra',    100000.00,  'đêm',   'Cho thuê crib / giường em bé',                                  1),
('Bánh sinh nhật / kỷ niệm',     'F&B',      350000.00,  'cái',   'Bánh theo yêu cầu — đặt trước 24h',                             1),
('Trang trí phòng hoa tươi',     'Extra',    500000.00,  'lần',   'Trang trí phòng với hoa tươi theo dịp đặc biệt',                 1),
('In tài liệu / Photocopy',      'Business',   5000.00,  'trang', 'Dịch vụ in ấn và photocopy tại Business Center',                1),
('Thuê phòng họp nhỏ (≤10 người)','Business',500000.00, 'giờ',   'Phòng họp 10 người với máy chiếu và WiFi tốc độ cao',            1),
('Phí hủy phòng',                'Extra',    500000.00,  'lần',   'Phí hủy đặt phòng không hoàn lại theo chính sách',              1);

-- ============================================================
-- 16. CHARGE (phụ thu / dịch vụ phát sinh)
-- ============================================================
INSERT INTO charge (reservation_id, service_id, quantity, unit_price, charge_date, staff_id, notes, is_voided) VALUES
-- Reservation 1 — Nguyễn Hoàng Minh (checked_out)
(1, 1,  4.00, 250000.00, '2026-05-21 07:30:00', 8, 'Buffet sáng 2 người × 2 ngày', 0),
(1, 7,  1.00, 600000.00, '2026-05-21 15:00:00', 8, 'Massage thư giãn 60 phút', 0),
(1, 9,  1.00, 350000.00, '2026-05-23 11:00:00', 2, 'Xe đưa sân bay Đà Nẵng', 0),
-- Reservation 2 — John Smith (checked_out)
(2, 1,  15.00, 250000.00, '2026-05-26 07:00:00', 8, 'Buffet sáng 3 người × 5 ngày', 0),
(2, 2,   6.00, 500000.00, '2026-05-27 19:00:00', 8, 'Bữa tối nhà hàng 2 người × 3 tối', 0),
(2, 13,  5.00, 100000.00, '2026-05-25 15:00:00', 3, 'Crib cho bé 5 đêm', 0),
(2, 9,   1.00, 350000.00, '2026-05-25 13:00:00', 2, 'Xe đón sân bay Đà Nẵng', 0),
-- Reservation 3 — Lê Đức Anh VIP (checked_out)
(3, 4,   2.00, 800000.00, '2026-06-01 19:30:00', 7, 'Rượu vang đỏ Châu Âu × 2 chai', 0),
(3, 8,   1.00, 900000.00, '2026-06-02 15:00:00', 8, 'Massage đá nóng 90 phút', 0),
(3, 17,  2.00, 500000.00, '2026-06-02 09:00:00', 7, 'Thuê phòng họp 2 giờ', 0),
(3, 5,   3.00,  50000.00, '2026-06-03 10:00:00', 5, 'Giặt đồ 3 món', 0),
-- Reservation 4 — Nguyễn Hoàng Minh (checked_in, đang ở)
(4, 11,  1.00, 200000.00, '2026-06-02 13:15:00', 2, 'Phí nhận phòng sớm', 0),
(4, 1,   4.00, 250000.00, '2026-06-03 07:30:00', 8, 'Buffet sáng 2 người × 2 ngày', 0),
(4, 3,   4.00, 120000.00, '2026-06-03 20:00:00', 8, 'Cocktail tại bar 4 ly', 0),
-- Reservation 5 — Yamamoto + Kim (checked_in, tuần trăng mật)
(5, 15,  1.00, 500000.00, '2026-06-03 14:00:00', 5, 'Trang trí phòng hoa hồng tuần trăng mật', 0),
(5, 14,  1.00, 350000.00, '2026-06-04 00:00:00', 8, 'Bánh kem kỷ niệm cặp đôi', 0),
(5, 7,   2.00, 600000.00, '2026-06-04 15:00:00', 8, 'Massage cặp đôi', 0),
-- Reservation 6 — Lê Đức Anh Presidential (checked_in hôm nay)
(6, 9,   1.00, 350000.00, '2026-06-04 11:30:00', 2, 'Xe đón sân bay từ Hà Nội', 0),
(6, 4,   3.00, 800000.00, '2026-06-04 19:00:00', 7, 'Rượu vang cao cấp × 3 chai', 0),
-- Reservation 11 — phí hủy (cancelled)
(11, 18, 1.00, 500000.00, '2026-05-28 11:00:00', 1, 'Phí hủy phòng theo chính sách', 0);

-- ============================================================
-- 17. INVOICE
-- ============================================================
-- Hóa đơn đã thanh toán đầy đủ
INSERT INTO invoice (invoice_code, reservation_id, issue_date, due_date, room_charges, service_charges, damage_charges, subtotal, discount_amount, tax_rate, tax_amount, total_amount, paid_amount, balance_due, currency, status, issued_by) VALUES
('INV-20260523-001', 1,  '2026-05-23 11:30:00', '2026-05-23',
  6300000.00, 1950000.00,      0.00,  8250000.00, 630000.00, 10.00,  762000.00,  8382000.00,  8382000.00,        0.00, 'VND', 'paid',           3),
('INV-20260530-002', 2,  '2026-05-30 11:00:00', '2026-05-30',
 12500000.00, 6425000.00,      0.00, 18925000.00,      0.00, 10.00, 1892500.00, 20817500.00, 20817500.00,        0.00, 'VND', 'paid',           2),
('INV-20260604-003', 3,  '2026-06-04 10:30:00', '2026-06-04',
 11400000.00, 3250000.00, 150000.00, 14800000.00, 1500000.00, 10.00, 1330000.00, 14630000.00, 14630000.00,       0.00, 'VND', 'paid',           2),
('INV-20260528-011', 11, '2026-05-28 11:30:00', '2026-05-28',
       0.00,   500000.00,      0.00,   500000.00,      0.00, 10.00,   50000.00,   550000.00,   550000.00,        0.00, 'VND', 'paid',           1);

-- Hóa đơn đang thanh toán một phần (draft / in-stay)
INSERT INTO invoice (invoice_code, reservation_id, issue_date, room_charges, service_charges, damage_charges, subtotal, discount_amount, tax_rate, tax_amount, total_amount, paid_amount, balance_due, currency, status, issued_by) VALUES
('INV-DRAFT-004', 4,  '2026-06-04 18:00:00',
  4000000.00, 1480000.00, 0.00,  5480000.00,      0.00, 10.00, 548000.00,  6028000.00,  3000000.00,  3028000.00, 'VND', 'partially_paid', 2),
('INV-DRAFT-005', 5,  '2026-06-04 18:00:00',
  5600000.00, 1450000.00, 0.00,  7050000.00, 1410000.00, 10.00, 564000.00,  6204000.00,  4000000.00,  2204000.00, 'VND', 'partially_paid', 3),
('INV-DRAFT-006', 6,  '2026-06-04 18:00:00',
 59500000.00, 2750000.00, 0.00, 62250000.00, 14875000.00, 10.00, 4737500.00, 52112500.00, 20000000.00, 32112500.00, 'VND', 'partially_paid', 1);

-- ============================================================
-- 18. PAYMENT (giao dịch thanh toán)
-- ============================================================
INSERT INTO payment (invoice_id, amount, payment_method, payment_date, transaction_ref, card_last4, card_type, is_deposit, status, processed_by, notes) VALUES
-- Invoice 1 (Res 1 — đã thanh toán đủ)
(1,  2000000.00, 'bank_transfer', '2026-05-18 10:00:00', 'TXN-MB-20260518-001',   NULL,   NULL,        1, 'completed', 2, 'Đặt cọc qua MB Bank'),
(1,  6382000.00, 'credit_card',   '2026-05-23 11:45:00', 'TXN-VISA-20260523-001', '4521', 'Visa',      0, 'completed', 3, 'Thanh toán cuối kỳ bằng thẻ Visa'),
-- Invoice 2 (Res 2 — đã thanh toán đủ)
(2,  5000000.00, 'bank_transfer', '2026-05-23 14:00:00', 'TXN-VCB-20260523-001',  NULL,   NULL,        1, 'completed', 2, 'Đặt cọc qua Vietcombank'),
(2, 15817500.00, 'credit_card',   '2026-05-30 11:15:00', 'TXN-MC-20260530-001',   '8832', 'Mastercard',0, 'completed', 2, 'Thanh toán bằng Mastercard'),
-- Invoice 3 (Res 3 VIP — đã thanh toán đủ)
(3,  5000000.00, 'bank_transfer', '2026-05-30 09:00:00', 'TXN-ACB-20260530-001',  NULL,   NULL,        1, 'completed', 1, 'Đặt cọc qua ACB'),
(3,  9630000.00, 'credit_card',   '2026-06-04 10:45:00', 'TXN-AMEX-20260604-001', '7731', 'Amex',      0, 'completed', 2, 'Thanh toán Amex Platinum'),
-- Invoice 4 (Res 11 hủy — phí hủy)
(4,   550000.00, 'cash',          '2026-05-28 11:45:00', NULL,                     NULL,   NULL,        0, 'completed', 1, 'Phí hủy phòng tiền mặt'),
-- Invoice 5 (Res 4 — đặt cọc)
(5,  3000000.00, 'bank_transfer', '2026-05-30 16:00:00', 'TXN-MB-20260530-002',   NULL,   NULL,        1, 'completed', 2, 'Đặt cọc qua MB Bank'),
-- Invoice 6 (Res 5 — đặt cọc)
(6,  4000000.00, 'bank_transfer', '2026-06-01 10:00:00', 'TXN-VCB-20260601-001',  NULL,   NULL,        1, 'completed', 2, 'Đặt cọc agoda'),
-- Invoice 7 (Res 6 VIP — đặt cọc lớn)
(7, 20000000.00, 'bank_transfer', '2026-06-01 14:00:00', 'TXN-ACB-20260601-002',  NULL,   NULL,        1, 'completed', 1, 'Đặt cọc Presidential Suite — khách VIP Lê Đức Anh');

-- ============================================================
-- 19. HOUSEKEEPING_TASK
-- ============================================================
INSERT INTO housekeeping_task (room_id, task_type, assigned_to, task_date, scheduled_time, started_at, completed_at, status, notes, checked_by) VALUES
-- 03/06/2026
(1,  'daily_cleaning',    5, '2026-06-03', '09:00:00', '2026-06-03 09:05:00', '2026-06-03 09:45:00', 'completed', NULL, 4),
(3,  'daily_cleaning',    5, '2026-06-03', '09:00:00', '2026-06-03 09:50:00', '2026-06-03 10:25:00', 'completed', NULL, 4),
(4,  'daily_cleaning',    6, '2026-06-03', '10:00:00', '2026-06-03 10:10:00', '2026-06-03 11:00:00', 'completed', 'Phòng đang có khách', 4),
(8,  'daily_cleaning',    6, '2026-06-03', '10:00:00', '2026-06-03 11:10:00', '2026-06-03 11:55:00', 'completed', NULL, 4),
(11, 'daily_cleaning',    5, '2026-06-03', '11:00:00', '2026-06-03 12:00:00', '2026-06-03 13:00:00', 'completed', 'Suite room — cần thêm thời gian', 4),
(14, 'daily_cleaning',    6, '2026-06-03', '13:00:00', '2026-06-03 13:05:00', '2026-06-03 14:30:00', 'completed', 'Presidential Suite — dọn kỹ lưỡng', 4),
-- 04/06/2026 (hôm nay)
(1,  'daily_cleaning',    5, '2026-06-04', '09:00:00', '2026-06-04 09:00:00', '2026-06-04 09:40:00', 'completed', NULL, 4),
(3,  'daily_cleaning',    5, '2026-06-04', '09:00:00', '2026-06-04 09:45:00', '2026-06-04 10:20:00', 'completed', NULL, 4),
(4,  'daily_cleaning',    6, '2026-06-04', '10:00:00', '2026-06-04 10:00:00', '2026-06-04 10:50:00', 'completed', 'Khách có mặt, được phép vào dọn', 4),
(6,  'checkout_cleaning', 5, '2026-06-04', '10:30:00', '2026-06-04 10:30:00', NULL,                  'in_progress','Phòng 203 vừa checkout — đang dọn', NULL),
(8,  'daily_cleaning',    6, '2026-06-04', '11:00:00', NULL,                  NULL,                  'pending',   NULL, NULL),
(11, 'daily_cleaning',    5, '2026-06-04', '11:00:00', NULL,                  NULL,                  'pending',   NULL, NULL),
(14, 'daily_cleaning',    6, '2026-06-04', '14:00:00', NULL,                  NULL,                  'pending',   'Presidential Suite — phối hợp butler', NULL),
(2,  'maintenance_check', 9, '2026-06-04', '09:00:00', '2026-06-04 09:15:00', '2026-06-04 10:30:00', 'completed', 'Kiểm tra điều hòa phòng 102', 4),
(5,  'turndown',          6, '2026-06-04', '18:00:00', NULL,                  NULL,                  'pending',   'Turndown service phòng 202', NULL);

-- ============================================================
-- 20. MINIBAR_ITEM (12 món)
-- ============================================================
INSERT INTO minibar_item (item_name, unit_price, category, is_active) VALUES
('Nước khoáng 500ml',              35000.00, 'Drink',    1),
('Nước ngọt Coca-Cola 330ml',      45000.00, 'Drink',    1),
('Bia Tiger 330ml',                55000.00, 'Drink',    1),
('Rượu vang mini 187ml',          150000.00, 'Drink',    1),
('Whisky miniature 50ml',         120000.00, 'Drink',    1),
('Nước ép trái cây 250ml',         60000.00, 'Drink',    1),
('Hạt điều rang muối',             80000.00, 'Snack',    1),
('Chocolate Ferrero Rocher (3 viên)',95000.00,'Snack',    1),
('Bánh quy cao cấp',               70000.00, 'Snack',    1),
('Mì ăn liền',                     40000.00, 'Snack',    1),
('Cà phê hòa tan cao cấp (gói)',   30000.00, 'Beverage', 1),
('Trà thảo mộc (gói)',             25000.00, 'Beverage', 1);

-- ============================================================
-- 21. MINIBAR_CONSUMPTION
-- ============================================================
INSERT INTO minibar_consumption (reservation_id, item_id, quantity, unit_price, recorded_at, recorded_by) VALUES
-- Reservation 1 (checked_out)
(1, 1, 4,  35000.00, '2026-05-22 18:00:00', 5),
(1, 3, 2,  55000.00, '2026-05-22 20:00:00', 5),
(1, 7, 1,  80000.00, '2026-05-22 21:00:00', 5),
-- Reservation 2 (checked_out)
(2, 1, 6,  35000.00, '2026-05-28 09:00:00', 5),
(2, 2, 3,  45000.00, '2026-05-27 15:00:00', 5),
(2, 10, 2, 40000.00, '2026-05-26 22:00:00', 5),
-- Reservation 3 (checked_out — VIP)
(3, 8, 2,  95000.00, '2026-06-02 21:00:00', 5),
(3, 5, 1, 120000.00, '2026-06-02 22:00:00', 5),
-- Reservation 4 (checked_in)
(4, 1, 2,  35000.00, '2026-06-03 23:00:00', 5),
(4, 3, 2,  55000.00, '2026-06-03 22:00:00', 5),
-- Reservation 5 (checked_in — tuần trăng mật)
(5, 4, 1, 150000.00, '2026-06-03 21:00:00', 6),
(5, 8, 2,  95000.00, '2026-06-03 22:30:00', 6),
-- Reservation 6 (checked_in — Presidential VIP)
(6, 4, 2, 150000.00, '2026-06-04 21:00:00', 6),
(6, 5, 1, 120000.00, '2026-06-04 22:00:00', 6);

-- ============================================================
-- 22. MAINTENANCE_REQUEST (6 sự cố)
-- ============================================================
INSERT INTO maintenance_request (room_id, issue_type, description, priority, status, reported_by, assigned_to, reported_at, started_at, resolved_at, resolution_note) VALUES
(2,  'Điều hòa',    'Điều hòa phòng 102 không lạnh, phát tiếng ồn bất thường khi chạy', 'high',   'in_progress', 5,  9,  '2026-06-03 08:30:00', '2026-06-04 09:15:00', NULL,                   NULL),
(8,  'Nước nóng',   'Vòi nước nóng trong phòng tắm chảy yếu áp',                         'medium', 'resolved',    6,  11, '2026-05-28 14:00:00', '2026-05-28 15:00:00', '2026-05-28 17:30:00', 'Đã thay joint cao su van nước nóng — áp suất trở lại bình thường'),
(14, 'Điện',        'Đèn phòng khách Presidential Suite nhấp nháy liên tục',             'urgent', 'resolved',    2,  9,  '2026-06-02 20:00:00', '2026-06-02 20:30:00', '2026-06-02 21:00:00', 'Đã thay bóng LED + kiểm tra dây điện — an toàn'),
(5,  'Khóa cửa',   'Khóa thẻ phòng 202 không nhận thẻ lần đầu, phải quẹt nhiều lần',   'low',    'open',        3,  11, '2026-06-04 09:00:00', NULL,                  NULL,                   NULL),
(1,  'Nước',        'Bồn rửa mặt phòng 101 thoát nước chậm',                             'low',    'resolved',    5,  11, '2026-06-01 10:00:00', '2026-06-01 14:00:00', '2026-06-01 15:00:00', 'Đã thông cống, vệ sinh lưới lọc'),
(4,  'TV',          'Remote TV phòng 201 mất điện/không phản hồi',                       'low',    'closed',      2,  9,  '2026-06-02 19:00:00', '2026-06-02 19:30:00', '2026-06-02 19:45:00', 'Đã thay pin AAA mới cho remote TV');

-- ============================================================
-- 23. REVIEW (đánh giá sau lưu trú)
-- ============================================================
INSERT INTO review (reservation_id, guest_id, overall_rating, cleanliness, service, location, value_for_money, comment, staff_reply, replied_by, replied_at, source, is_published) VALUES
(1, 1, 5, 5, 5, 5, 4,
 'Khách sạn tuyệt vời! Phòng sạch sẽ và sang trọng. Nhân viên lễ tân cực kỳ chu đáo — đặc biệt bạn Bình rất thân thiện. Sẽ quay lại lần sau!',
 'Xin cảm ơn anh Minh đã tin tưởng và chia sẻ đánh giá tích cực! Chúng tôi rất vui khi anh có trải nghiệm tuyệt vời. Hân hạnh được đón anh trở lại!',
 1, '2026-05-25 10:00:00', 'internal', 1),
(2, 5, 4, 4, 5, 5, 4,
 'Great hotel with amazing sea view. Staff are very helpful and professional. The breakfast buffet had many options. Slightly pricey but worth it for the experience. Family-friendly!',
 'Thank you Mr. Smith for your wonderful review! We are delighted you enjoyed your family stay with us. We hope to welcome you back soon!',
 1, '2026-06-02 09:00:00', 'booking_com', 1),
(3, 3, 5, 5, 5, 5, 5,
 'Đây là lần thứ 25 tôi lưu trú tại đây và lần nào cũng hoàn hảo. Senior Suite view biển cực đẹp. Đội ngũ nhớ sở thích của tôi từ những lần trước. Xứng đáng 5 sao!',
 NULL, NULL, NULL, 'internal', 1);

-- ============================================================
-- 24. AUDIT_LOG (nhật ký thao tác)
-- ============================================================
INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, performed_by, performed_at, ip_address, notes) VALUES
('Reservation', 11, 'UPDATE',
 '{"status":"confirmed"}',
 '{"status":"cancelled","cancel_reason":"Khách đổi lịch công tác đột xuất","cancelled_at":"2026-05-28 10:30:00"}',
 1, '2026-05-28 10:30:00', '192.168.1.101', 'Hủy đặt phòng RES-20260525-011 theo yêu cầu khách'),
('Guest', 3, 'UPDATE',
 '{"loyalty_tier":"Gold","loyalty_points":7500,"total_stays":24}',
 '{"loyalty_tier":"Platinum","loyalty_points":8500,"total_stays":25}',
 1, '2026-06-04 10:00:00', '192.168.1.101', 'Nâng hạng Platinum sau lần lưu trú thứ 25 của Mr. Lê Đức Anh'),
('Room', 2, 'UPDATE',
 '{"status":"available"}',
 '{"status":"maintenance","notes":"Đang sửa điều hòa — dự kiến xong 5/6"}',
 9, '2026-06-03 08:35:00', '192.168.1.110', 'Chuyển phòng 102 sang bảo trì do sự cố điều hòa'),
('Payment', 2, 'INSERT',
 NULL,
 '{"invoice_id":1,"amount":6382000,"payment_method":"credit_card","status":"completed"}',
 3, '2026-05-23 11:45:00', '192.168.1.102', 'Thanh toán checkout phòng 201 — Nguyễn Hoàng Minh'),
('Room_Type_Promotion', 7, 'UPDATE',
 '{"used_count":2}',
 '{"used_count":3}',
 2, '2026-06-03 09:00:00', '192.168.1.102', 'Cập nhật used_count Flash Sale Hè sau đặt phòng mới'),
('Reservation', 6, 'INSERT',
 NULL,
 '{"reservation_code":"RES-20260604-006","guest_id":3,"room_id":14,"status":"confirmed"}',
 1, '2026-06-04 11:00:00', '192.168.1.101', 'Đặt phòng Presidential Suite cho khách VIP Lê Đức Anh');
