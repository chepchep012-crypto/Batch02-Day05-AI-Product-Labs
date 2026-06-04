-- ============================================================
--  DATABASE: AI GỢI Ý LỊCH TRÌNH DU LỊCH VINPEARL
--  Phạm vi: Toàn bộ hệ thống Vinpearl
--  Prototype: Hỏi 3 câu → Timeline 2N1Đ + Phòng + Ưu đãi
--  Nhóm: Phạm Thị Tuyết Nga, Nguyễn Thái Hoàng,
--         Nguyễn Đức Toàn, Nguyễn Ngô Huy Tùng Anh
-- ============================================================

CREATE DATABASE IF NOT EXISTS vinpearl_itinerary
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE vinpearl_itinerary;

-- ============================================================
-- NHÓM 1: ĐỊA ĐIỂM DU LỊCH VINPEARL
-- ============================================================

CREATE TABLE Destination (
    destination_id      INT             AUTO_INCREMENT PRIMARY KEY,
    destination_name    VARCHAR(200)    NOT NULL,
    province            VARCHAR(100)    NOT NULL,
    region              ENUM('north','central','south') NOT NULL,
    description         TEXT,
    best_months         VARCHAR(100),
    avg_trip_days       TINYINT         DEFAULT 2,
    thumbnail_url       VARCHAR(500),
    is_active           TINYINT(1)      NOT NULL DEFAULT 1
);

CREATE TABLE Resort (
    resort_id           INT             AUTO_INCREMENT PRIMARY KEY,
    destination_id      INT             NOT NULL,
    resort_name         VARCHAR(200)    NOT NULL,
    resort_code         VARCHAR(30)     NOT NULL UNIQUE,
    resort_type         ENUM('resort','discovery','safari','grand_world','condotel') NOT NULL,
    address             TEXT,
    distance_to_center_km DECIMAL(5,1),
    amenities           TEXT,
    source_url          VARCHAR(500)    NOT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    CONSTRAINT fk_resort_dest FOREIGN KEY (destination_id)
        REFERENCES Destination(destination_id)
);

CREATE TABLE Room_Type (
    room_type_id        INT             AUTO_INCREMENT PRIMARY KEY,
    resort_id           INT             NOT NULL,
    type_name           VARCHAR(200)    NOT NULL,
    capacity_adults     INT             NOT NULL DEFAULT 2,
    capacity_children   INT             NOT NULL DEFAULT 0,
    area_sqm            DECIMAL(6,1),
    view_type           VARCHAR(100),
    suitable_for        VARCHAR(200),
    budget_level        ENUM('mid','luxury','ultra') NOT NULL DEFAULT 'mid',
    price_per_night     DECIMAL(12,2)   NOT NULL,
    price_currency      VARCHAR(3)      NOT NULL DEFAULT 'VND',
    breakfast_included  TINYINT(1)      NOT NULL DEFAULT 0,
    source_url          VARCHAR(500)    NOT NULL,
    thumbnail_url       VARCHAR(500),
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    CONSTRAINT fk_rt_resort FOREIGN KEY (resort_id)
        REFERENCES Resort(resort_id)
);

-- ============================================================
-- NHÓM 2: ƯU ĐÃI / KHUYẾN MÃI
-- ============================================================

CREATE TABLE Promotion (
    promotion_id        INT             AUTO_INCREMENT PRIMARY KEY,
    destination_id      INT             DEFAULT NULL,
    resort_id           INT             DEFAULT NULL,
    promotion_name      VARCHAR(300)    NOT NULL,
    discount_type       ENUM('percentage','fixed_amount','combo','free_night') NOT NULL,
    discount_value      DECIMAL(10,2)   NOT NULL,
    valid_from          DATE            NOT NULL,
    valid_to            DATE            NOT NULL,
    applicable_days     VARCHAR(100)    DEFAULT 'All',
    min_nights          INT             NOT NULL DEFAULT 1,
    applicable_room_types VARCHAR(500)  DEFAULT 'All',
    conditions          TEXT,
    source_url          VARCHAR(500)    NOT NULL,
    is_verified         TINYINT(1)      NOT NULL DEFAULT 1,
    last_verified_at    DATETIME        NOT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    CONSTRAINT fk_promo_dest   FOREIGN KEY (destination_id) REFERENCES Destination(destination_id),
    CONSTRAINT fk_promo_resort FOREIGN KEY (resort_id)      REFERENCES Resort(resort_id)
);

-- ============================================================
-- NHÓM 3: ĐỊA ĐIỂM THAM QUAN & HOẠT ĐỘNG
-- ============================================================

CREATE TABLE Attraction (
    attraction_id       INT             AUTO_INCREMENT PRIMARY KEY,
    destination_id      INT             NOT NULL,
    attraction_name     VARCHAR(200)    NOT NULL,
    category            VARCHAR(100)    NOT NULL,
    suitable_for        VARCHAR(200),
    suitable_budget     ENUM('budget','mid','luxury','all') DEFAULT 'all',
    suitable_preference VARCHAR(200),
    open_time           TIME            NOT NULL,
    close_time          TIME            NOT NULL,
    open_days           VARCHAR(100)    DEFAULT 'All',
    duration_hours      DECIMAL(4,1)    NOT NULL,
    entry_fee_adult     DECIMAL(10,2)   DEFAULT 0,
    entry_fee_child     DECIMAL(10,2)   DEFAULT 0,
    entry_fee_note      VARCHAR(300),
    location_area       VARCHAR(100),
    notes               TEXT,
    source_url          VARCHAR(500)    NOT NULL,
    is_active           TINYINT(1)      NOT NULL DEFAULT 1,
    CONSTRAINT fk_attr_dest FOREIGN KEY (destination_id)
        REFERENCES Destination(destination_id)
);

CREATE TABLE Travel_Matrix (
    matrix_id           INT             AUTO_INCREMENT PRIMARY KEY,
    destination_id      INT             NOT NULL,
    from_location       VARCHAR(200)    NOT NULL,
    to_location         VARCHAR(200)    NOT NULL,
    transport_type      VARCHAR(100)    NOT NULL,
    duration_minutes    INT             NOT NULL,
    distance_km         DECIMAL(5,1),
    cost_estimate_vnd   DECIMAL(10,2)   DEFAULT 0,
    notes               VARCHAR(300),
    CONSTRAINT fk_tm_dest FOREIGN KEY (destination_id)
        REFERENCES Destination(destination_id)
);

-- ============================================================
-- NHÓM 4: SESSION & INPUT NGƯỜI DÙNG
-- ============================================================

CREATE TABLE User_Session (
    session_id          INT             AUTO_INCREMENT PRIMARY KEY,
    session_token       VARCHAR(100)    NOT NULL UNIQUE,
    started_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at        DATETIME,
    status              ENUM('in_progress','completed','abandoned') DEFAULT 'in_progress'
);

CREATE TABLE User_Input (
    input_id            INT             AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    destination_id      INT             NOT NULL,
    travel_group        ENUM('solo','couple','family_kids',
                            'family_no_kids','group_friends') NOT NULL,
    num_adults          INT             NOT NULL DEFAULT 2,
    num_children        INT             NOT NULL DEFAULT 0,
    children_ages       VARCHAR(100),
    budget_level        ENUM('mid','luxury') NOT NULL,
    budget_per_night    DECIMAL(12,2),
    preference          ENUM('beach','entertainment','nature','food','mix') NOT NULL,
    checkin_date        DATE,
    checkout_date       DATE,
    is_clarified        TINYINT(1)      NOT NULL DEFAULT 0,
    clarification_field VARCHAR(50),
    clarification_question VARCHAR(500),
    clarification_answer   VARCHAR(500),
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ui_session FOREIGN KEY (session_id)
        REFERENCES User_Session(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_ui_dest FOREIGN KEY (destination_id)
        REFERENCES Destination(destination_id)
);

-- ============================================================
-- NHÓM 5: OUTPUT — LỊCH TRÌNH AI GỢI Ý
-- ============================================================

CREATE TABLE Itinerary (
    itinerary_id        INT             AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    destination_id      INT             NOT NULL,
    generated_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    room_type_id        INT             NOT NULL,
    room_reason         TEXT            NOT NULL,
    promotion_id        INT             DEFAULT NULL,
    promotion_reason    TEXT,
    no_promotion_reason TEXT,
    estimated_cost_min  DECIMAL(12,2),
    estimated_cost_max  DECIMAL(12,2),
    confidence_score    TINYINT         DEFAULT 100,
    status              ENUM('generated','accepted','modified','rejected') DEFAULT 'generated',
    CONSTRAINT fk_itin_session   FOREIGN KEY (session_id)    REFERENCES User_Session(session_id),
    CONSTRAINT fk_itin_dest      FOREIGN KEY (destination_id) REFERENCES Destination(destination_id),
    CONSTRAINT fk_itin_room      FOREIGN KEY (room_type_id)  REFERENCES Room_Type(room_type_id),
    CONSTRAINT fk_itin_promo     FOREIGN KEY (promotion_id)  REFERENCES Promotion(promotion_id)
);

CREATE TABLE Itinerary_Timeline (
    timeline_id         INT             AUTO_INCREMENT PRIMARY KEY,
    itinerary_id        INT             NOT NULL,
    day_number          TINYINT         NOT NULL,
    time_slot           ENUM('morning','afternoon','evening','night') NOT NULL,
    start_time          TIME            NOT NULL,
    end_time            TIME            NOT NULL,
    attraction_id       INT             NOT NULL,
    activity_note       TEXT,
    ai_reason           TEXT            NOT NULL,
    travel_to_next_min  INT             DEFAULT 0,
    order_in_day        INT             NOT NULL,
    CONSTRAINT fk_itl_itinerary  FOREIGN KEY (itinerary_id)  REFERENCES Itinerary(itinerary_id),
    CONSTRAINT fk_itl_attraction FOREIGN KEY (attraction_id) REFERENCES Attraction(attraction_id)
);

-- ============================================================
-- NHÓM 6: CORRECTION & FEEDBACK
-- ============================================================

CREATE TABLE User_Correction (
    correction_id       INT             AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    itinerary_id        INT             NOT NULL,
    correction_type     ENUM('change_destination','change_preference',
                            'change_budget','change_group',
                            'change_date','other') NOT NULL,
    old_value           VARCHAR(500)    NOT NULL,
    new_value           VARCHAR(500)    NOT NULL,
    corrected_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    new_itinerary_id    INT,
    CONSTRAINT fk_uc_session  FOREIGN KEY (session_id)       REFERENCES User_Session(session_id),
    CONSTRAINT fk_uc_itin     FOREIGN KEY (itinerary_id)     REFERENCES Itinerary(itinerary_id),
    CONSTRAINT fk_uc_new_itin FOREIGN KEY (new_itinerary_id) REFERENCES Itinerary(itinerary_id)
);

CREATE TABLE User_Feedback (
    feedback_id         INT             AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    itinerary_id        INT             NOT NULL,
    rating              TINYINT         NOT NULL,
    found_useful        TINYINT(1),
    promotion_accurate  TINYINT(1),
    comment             TEXT,
    submitted_at        DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_uf_session   FOREIGN KEY (session_id)   REFERENCES User_Session(session_id),
    CONSTRAINT fk_uf_itinerary FOREIGN KEY (itinerary_id) REFERENCES Itinerary(itinerary_id),
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5)
);

-- ============================================================
-- NHÓM 7: AI AUDIT LOG
-- ============================================================

CREATE TABLE AI_Decision_Log (
    log_id              BIGINT          AUTO_INCREMENT PRIMARY KEY,
    session_id          INT             NOT NULL,
    decision_type       ENUM('destination_match','room_selection',
                            'promotion_selection','timeline_slot',
                            'clarification_ask','no_promotion_response') NOT NULL,
    input_context       JSON            NOT NULL,
    output_decision     JSON            NOT NULL,
    data_source_ids     VARCHAR(200),
    is_hallucination    TINYINT(1)      NOT NULL DEFAULT 0,
    confidence          TINYINT         DEFAULT 100,
    logged_at           DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_adl_session FOREIGN KEY (session_id)
        REFERENCES User_Session(session_id)
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_resort_dest      ON Resort(destination_id, is_active);
CREATE INDEX idx_room_resort      ON Room_Type(resort_id, budget_level);
CREATE INDEX idx_promo_dates      ON Promotion(valid_from, valid_to, is_active);
CREATE INDEX idx_promo_dest       ON Promotion(destination_id, resort_id);
CREATE INDEX idx_attr_dest_pref   ON Attraction(destination_id, suitable_preference);
CREATE INDEX idx_ui_dest          ON User_Input(destination_id);
CREATE INDEX idx_itin_session     ON Itinerary(session_id);
CREATE INDEX idx_timeline_day     ON Itinerary_Timeline(itinerary_id, day_number);
CREATE INDEX idx_ai_log           ON AI_Decision_Log(session_id, decision_type);

-- ============================================================
-- VIEWS
-- ============================================================

CREATE VIEW v_active_promotions AS
SELECT p.*, d.destination_name, r.resort_name
FROM Promotion p
LEFT JOIN Destination d ON p.destination_id = d.destination_id
LEFT JOIN Resort r       ON p.resort_id      = r.resort_id
WHERE p.is_active = 1
  AND p.is_verified = 1
  AND CURDATE() BETWEEN p.valid_from AND p.valid_to;

CREATE VIEW v_family_rooms AS
SELECT rt.*, r.resort_name, d.destination_name
FROM Room_Type rt
JOIN Resort r      ON rt.resort_id      = r.resort_id
JOIN Destination d ON r.destination_id  = d.destination_id
WHERE rt.capacity_children >= 1 AND rt.is_active = 1;

CREATE VIEW v_destination_summary AS
SELECT
    d.destination_id, d.destination_name, d.province, d.region,
    COUNT(DISTINCT r.resort_id)    AS total_resorts,
    COUNT(DISTINCT p.promotion_id) AS active_promotions
FROM Destination d
LEFT JOIN Resort r    ON d.destination_id = r.destination_id AND r.is_active = 1
LEFT JOIN Promotion p ON (p.destination_id = d.destination_id OR p.destination_id IS NULL)
                      AND p.is_active = 1
                      AND CURDATE() BETWEEN p.valid_from AND p.valid_to
WHERE d.is_active = 1
GROUP BY d.destination_id;

-- ============================================================
-- MOCK DATA
-- ============================================================

-- ------------------------------------------------------------
-- 1. DESTINATION (5 điểm đến)
-- ------------------------------------------------------------
INSERT INTO Destination (destination_name, province, region, description, best_months, avg_trip_days, thumbnail_url) VALUES
('Phú Quốc',   'Kiên Giang', 'south',
 'Đảo ngọc Phú Quốc — thiên đường biển với hệ sinh thái san hô phong phú, VinWonders và Safari đẳng cấp quốc tế.',
 '11-4', 3, 'https://vinpearl.com/images/destinations/phu-quoc.jpg'),
('Nha Trang',  'Khánh Hòa',  'central',
 'Thành phố biển sầm uất với cáp treo vượt biển dài nhất thế giới, VinWonders Nha Trang và chuỗi đảo hoang sơ.',
 '1-8',  3, 'https://vinpearl.com/images/destinations/nha-trang.jpg'),
('Nam Hội An', 'Quảng Nam',  'central',
 'Khu nghỉ dưỡng sinh thái hòa quyện văn hoá Hội An cổ kính — bãi biển trong xanh và VinWonders đa sắc màu.',
 '2-7',  2, 'https://vinpearl.com/images/destinations/nam-hoi-an.jpg'),
('Cửa Hội',   'Nghệ An',    'central',
 'Điểm nghỉ dưỡng biển mới nổi tại miền Trung — gần di sản Nghệ An, hải sản tươi ngon và bãi biển Cửa Lò.',
 '5-8',  2, 'https://vinpearl.com/images/destinations/cua-hoi.jpg'),
('Hải Phòng',  'Hải Phòng',  'north',
 'Thành phố cảng phía Bắc với sân golf Vinpearl đẳng cấp, gần quần đảo Cát Bà — vịnh Hạ Long mini.',
 '4-10', 2, 'https://vinpearl.com/images/destinations/hai-phong.jpg');

-- ------------------------------------------------------------
-- 2. RESORT (9 khu resort)
-- ------------------------------------------------------------
INSERT INTO Resort (destination_id, resort_name, resort_code, resort_type, address, distance_to_center_km, amenities, source_url) VALUES
(1, 'Vinpearl Resort & Spa Phú Quốc',   'VPR_PQ',    'resort',
 'Bãi Dài, Gành Dầu, Phú Quốc, Kiên Giang', 18.0,
 'Bãi biển riêng, 5 hồ bơi, Spa 5 sao, 6 nhà hàng, phòng gym, sân tennis, khu vui chơi trẻ em',
 'https://vinpearl.com/vi/resort-spa-phu-quoc'),
(1, 'Vinpearl Discovery 1 Phú Quốc',    'VPD1_PQ',   'discovery',
 'Gành Dầu, Phú Quốc, Kiên Giang', 20.0,
 'Bungalow gần biển, hồ bơi vô cực, nhà hàng ẩm thực quốc tế, xe đạp miễn phí',
 'https://vinpearl.com/vi/discovery-1-phu-quoc'),
(1, 'Vinpearl Grand World Phú Quốc',    'VPGW_PQ',   'grand_world',
 'Bãi Dài, Phú Quốc, Kiên Giang', 17.0,
 'Condotel cao cấp, khu Grand World 4 mùa, casino, trung tâm thương mại, hồ bơi vô cực',
 'https://vinpearl.com/vi/grand-world-phu-quoc'),
(1, 'Vinpearl Safari Resort Phú Quốc',  'VPSR_PQ',   'safari',
 'Khu Safari, Phú Quốc, Kiên Giang', 16.0,
 'Bungalow trong rừng, hồ bơi thiên nhiên, tour safari riêng, nhà hàng BBQ ngoài trời',
 'https://vinpearl.com/vi/safari-resort-phu-quoc'),
(2, 'Vinpearl Resort & Spa Nha Trang',  'VPR_NT',    'resort',
 'Đảo Hòn Tre, Nha Trang, Khánh Hòa', 5.0,
 'Bãi biển riêng, 3 hồ bơi, Spa, cáp treo vào đảo, 4 nhà hàng, khu vui chơi VinWonders',
 'https://vinpearl.com/vi/resort-spa-nha-trang'),
(2, 'Vinpearl Luxury Nha Trang',        'VPL_NT',    'resort',
 'Đảo Hòn Tre, Nha Trang, Khánh Hòa', 5.0,
 'Hồ bơi riêng mỗi villa, butler 24/7, bãi biển exclusive, nhà hàng fine dining, Spa cao cấp',
 'https://vinpearl.com/vi/luxury-nha-trang'),
(3, 'Vinpearl Nam Hội An',              'VP_NHA',    'resort',
 'Tây An, Duy Xuyên, Quảng Nam', 30.0,
 'Bãi biển riêng 3.5km, 4 hồ bơi, VinWonders Nam Hội An, Spa, xe điện nội khu, nhà hàng ẩm thực Hội An',
 'https://vinpearl.com/vi/nam-hoi-an'),
(4, 'Vinpearl Cửa Hội Resort & Villas', 'VP_CH',     'resort',
 'Cửa Hội, Nghi Xuân, Nghệ An', 2.0,
 'Bãi biển Cửa Lò sát resort, hồ bơi ngoài trời, nhà hàng hải sản, phòng gym, sân cầu lông',
 'https://vinpearl.com/vi/cua-hoi'),
(5, 'Vinpearl Resort & Golf Hải Phòng', 'VP_HP',     'resort',
 'Đảo Vũ Yên, Hải Phòng', 8.0,
 'Sân golf 18 lỗ championship, hồ bơi, bãi biển riêng, nhà hàng seafood, spa, câu lạc bộ golf',
 'https://vinpearl.com/vi/hai-phong');

-- ------------------------------------------------------------
-- 3. ROOM_TYPE (21 loại phòng — 2-3 loại/resort)
-- ------------------------------------------------------------
INSERT INTO Room_Type (resort_id, type_name, capacity_adults, capacity_children, area_sqm, view_type, suitable_for, budget_level, price_per_night, breakfast_included, source_url, thumbnail_url) VALUES
-- Resort 1: VPR_PQ
(1, 'Deluxe Sea View Phú Quốc',       2, 0, 42.0, 'Biển',    'Cặp đôi, Solo',           'mid',    2800000.00, 1, 'https://vinpearl.com/vi/resort-spa-phu-quoc/phong/deluxe-sea-view',    'https://vinpearl.com/images/rooms/vpr_pq_deluxe.jpg'),
(1, 'Family Suite Phú Quốc',          2, 2, 65.0, 'Vườn',    'Gia đình có trẻ nhỏ',     'mid',    4200000.00, 1, 'https://vinpearl.com/vi/resort-spa-phu-quoc/phong/family-suite',        'https://vinpearl.com/images/rooms/vpr_pq_family.jpg'),
(1, 'Beachfront Pool Villa Phú Quốc', 2, 1, 95.0, 'Biển',    'Cặp đôi',                 'luxury', 7200000.00, 1, 'https://vinpearl.com/vi/resort-spa-phu-quoc/phong/pool-villa',          'https://vinpearl.com/images/rooms/vpr_pq_villa.jpg'),
-- Resort 2: VPD1_PQ
(2, 'Discovery Deluxe Bungalow',      2, 0, 38.0, 'Biển',    'Cặp đôi, Nhóm bạn, Solo', 'mid',    2500000.00, 1, 'https://vinpearl.com/vi/discovery-1-phu-quoc/phong/deluxe-bungalow',   'https://vinpearl.com/images/rooms/vpd1_pq_deluxe.jpg'),
(2, 'Discovery Family Bungalow',      2, 2, 55.0, 'Vườn',    'Gia đình có trẻ nhỏ',     'mid',    3600000.00, 1, 'https://vinpearl.com/vi/discovery-1-phu-quoc/phong/family-bungalow',   'https://vinpearl.com/images/rooms/vpd1_pq_family.jpg'),
-- Resort 3: VPGW_PQ
(3, 'Grand World Studio',             2, 0, 35.0, 'Thành phố','Cặp đôi, Solo, Nhóm bạn','mid',    2200000.00, 0, 'https://vinpearl.com/vi/grand-world-phu-quoc/phong/studio',             'https://vinpearl.com/images/rooms/vpgw_pq_studio.jpg'),
(3, 'Grand World 1BR Suite',          2, 2, 68.0, 'Biển',    'Gia đình, Cặp đôi',        'luxury', 5500000.00, 1, 'https://vinpearl.com/vi/grand-world-phu-quoc/phong/1br-suite',          'https://vinpearl.com/images/rooms/vpgw_pq_suite.jpg'),
-- Resort 4: VPSR_PQ
(4, 'Safari Tent Lodge',              2, 1, 50.0, 'Rừng',    'Gia đình, Cặp đôi',        'luxury', 5800000.00, 1, 'https://vinpearl.com/vi/safari-resort-phu-quoc/phong/tent-lodge',      'https://vinpearl.com/images/rooms/vpsr_pq_tent.jpg'),
(4, 'Jungle View Deluxe',             2, 0, 40.0, 'Rừng',    'Cặp đôi, Nhóm bạn',        'mid',    3200000.00, 1, 'https://vinpearl.com/vi/safari-resort-phu-quoc/phong/jungle-view',     'https://vinpearl.com/images/rooms/vpsr_pq_jungle.jpg'),
-- Resort 5: VPR_NT
(5, 'Sea View Deluxe Nha Trang',      2, 0, 40.0, 'Biển',    'Cặp đôi, Solo',             'mid',    2600000.00, 1, 'https://vinpearl.com/vi/resort-spa-nha-trang/phong/sea-view-deluxe',   'https://vinpearl.com/images/rooms/vpr_nt_deluxe.jpg'),
(5, 'Family Deluxe Nha Trang',        2, 2, 60.0, 'Biển',    'Gia đình có trẻ nhỏ',       'mid',    3800000.00, 1, 'https://vinpearl.com/vi/resort-spa-nha-trang/phong/family-deluxe',     'https://vinpearl.com/images/rooms/vpr_nt_family.jpg'),
(5, 'Premium Suite Nha Trang',        2, 1, 75.0, 'Biển',    'Cặp đôi, Gia đình',         'luxury', 5200000.00, 1, 'https://vinpearl.com/vi/resort-spa-nha-trang/phong/premium-suite',     'https://vinpearl.com/images/rooms/vpr_nt_premium.jpg'),
-- Resort 6: VPL_NT
(6, 'Luxury Sea View Villa NT',       2, 0, 90.0, 'Biển',    'Cặp đôi',                   'luxury', 7500000.00, 1, 'https://vinpearl.com/vi/luxury-nha-trang/phong/sea-view-villa',        'https://vinpearl.com/images/rooms/vpl_nt_seaview.jpg'),
(6, 'Luxury Pool Villa NT',           2, 1, 130.0,'Hồ bơi',  'Cặp đôi, Gia đình nhỏ',    'ultra',  12000000.00,1, 'https://vinpearl.com/vi/luxury-nha-trang/phong/pool-villa',            'https://vinpearl.com/images/rooms/vpl_nt_poolvilla.jpg'),
-- Resort 7: VP_NHA
(7, 'Hội An Deluxe Garden Room',      2, 0, 38.0, 'Vườn',    'Cặp đôi, Solo',             'mid',    2400000.00, 1, 'https://vinpearl.com/vi/nam-hoi-an/phong/deluxe-garden',               'https://vinpearl.com/images/rooms/vp_nha_garden.jpg'),
(7, 'Hội An Family Room',             2, 2, 58.0, 'Vườn',    'Gia đình có trẻ nhỏ',       'mid',    3600000.00, 1, 'https://vinpearl.com/vi/nam-hoi-an/phong/family-room',                 'https://vinpearl.com/images/rooms/vp_nha_family.jpg'),
(7, 'Hội An Pool Suite',              2, 1, 80.0, 'Hồ bơi',  'Cặp đôi',                   'luxury', 5200000.00, 1, 'https://vinpearl.com/vi/nam-hoi-an/phong/pool-suite',                  'https://vinpearl.com/images/rooms/vp_nha_suite.jpg'),
-- Resort 8: VP_CH
(8, 'Beach View Deluxe Cửa Hội',     2, 0, 36.0, 'Biển',    'Cặp đôi, Solo',             'mid',    1800000.00, 1, 'https://vinpearl.com/vi/cua-hoi/phong/beach-view-deluxe',              'https://vinpearl.com/images/rooms/vp_ch_deluxe.jpg'),
(8, 'Ocean Suite Cửa Hội',            2, 1, 55.0, 'Biển',    'Gia đình, Cặp đôi',         'mid',    2800000.00, 1, 'https://vinpearl.com/vi/cua-hoi/phong/ocean-suite',                    'https://vinpearl.com/images/rooms/vp_ch_suite.jpg'),
-- Resort 9: VP_HP
(9, 'Golf View Deluxe Hải Phòng',    2, 0, 40.0, 'Sân Golf', 'Cặp đôi, Solo',             'mid',    2200000.00, 1, 'https://vinpearl.com/vi/hai-phong/phong/golf-view-deluxe',             'https://vinpearl.com/images/rooms/vp_hp_golf.jpg'),
(9, 'Ocean Suite Hải Phòng',          2, 1, 65.0, 'Biển',    'Cặp đôi, Gia đình nhỏ',    'luxury', 4500000.00, 1, 'https://vinpearl.com/vi/hai-phong/phong/ocean-suite',                  'https://vinpearl.com/images/rooms/vp_hp_ocean.jpg');

-- ------------------------------------------------------------
-- 4. PROMOTION (8 chương trình ưu đãi)
-- ------------------------------------------------------------
INSERT INTO Promotion (destination_id, resort_id, promotion_name, discount_type, discount_value, valid_from, valid_to, applicable_days, min_nights, applicable_room_types, conditions, source_url, is_verified, last_verified_at) VALUES
-- Promo 1: Hè Vàng Phú Quốc — toàn bộ resort tại Phú Quốc, mùa hè 2026
(1, NULL, 'Hè Vàng Phú Quốc 2026', 'percentage', 20.00,
 '2026-06-01', '2026-08-31', 'All', 2, 'All',
 'Giảm 20% giá phòng khi đặt từ 2 đêm trở lên tại bất kỳ resort Vinpearl Phú Quốc trong mùa hè 2026. Áp dụng tất cả loại phòng.',
 'https://vinpearl.com/vi/khuyen-mai/he-vang-phu-quoc-2026',
 1, '2026-06-01 08:00:00'),
-- Promo 2: Ưu đãi cặp đôi tại VPR_NT
(NULL, 5, 'Vinpearl Nha Trang — Ưu Đãi Cặp Đôi', 'percentage', 15.00,
 '2026-05-01', '2026-09-30', 'All', 2, 'All',
 'Giảm 15% cho cặp đôi lưu trú từ 2 đêm tại Vinpearl Resort & Spa Nha Trang. Tặng kèm buổi ăn tối lãng mạn trị giá 500.000 VND.',
 'https://vinpearl.com/vi/khuyen-mai/couple-nha-trang',
 1, '2026-06-01 08:00:00'),
-- Promo 3: Combo gia đình Safari Phú Quốc
(NULL, 4, 'Safari Family Package Phú Quốc', 'combo', 25.00,
 '2026-01-01', '2026-12-31', 'All', 2, 'All',
 'Combo gia đình: giảm 25% giá phòng + vé Safari miễn phí cho 2 trẻ em dưới 12 tuổi. Áp dụng tối thiểu 2 đêm.',
 'https://vinpearl.com/vi/khuyen-mai/safari-family-package',
 1, '2026-06-01 08:00:00'),
-- Promo 4: Early Bird 10 ngày — toàn hệ thống
(NULL, NULL, 'Early Bird Vinpearl — Đặt Sớm Giảm 10%', 'percentage', 10.00,
 '2026-01-01', '2026-12-31', 'All', 1, 'All',
 'Giảm 10% khi đặt phòng trước ít nhất 10 ngày so với ngày check-in. Áp dụng toàn hệ thống Vinpearl.',
 'https://vinpearl.com/vi/khuyen-mai/early-bird',
 1, '2026-06-01 08:00:00'),
-- Promo 5: Hội An Sunset Package — Oct-Dec 2026
(NULL, 7, 'Hội An Sunset Package', 'free_night', 1.00,
 '2026-10-01', '2026-12-31', 'All', 3,
 'All',
 'Ở 3 đêm tặng 1 đêm miễn phí tại Vinpearl Nam Hội An. Bao gồm tour phố cổ Hội An ban đêm miễn phí.',
 'https://vinpearl.com/vi/khuyen-mai/hoi-an-sunset-package',
 1, '2026-06-01 08:00:00'),
-- Promo 6: Luxury Summer NT — VPL_NT
(NULL, 6, 'Luxury Summer Nha Trang 2026', 'percentage', 20.00,
 '2026-07-01', '2026-08-31', 'All', 2, 'All',
 'Giảm 20% villa & suite tại Vinpearl Luxury Nha Trang mùa hè 2026. Tặng kèm dịch vụ spa 60 phút/người.',
 'https://vinpearl.com/vi/khuyen-mai/luxury-summer-nha-trang',
 1, '2026-06-01 08:00:00'),
-- Promo 7: Cửa Hội Biển Xanh — resort 8
(NULL, 8, 'Cửa Hội Biển Xanh Hè 2026', 'fixed_amount', 300000.00,
 '2026-06-01', '2026-08-31', 'All', 2, 'All',
 'Giảm 300.000 VND/đêm khi đặt từ 2 đêm tại Vinpearl Cửa Hội Resort & Villas. Tặng kèm tour Đảo Ngư miễn phí.',
 'https://vinpearl.com/vi/khuyen-mai/cua-hoi-bien-xanh',
 1, '2026-06-01 08:00:00'),
-- Promo 8: Vinpearl Golf HP Package — resort 9
(NULL, 9, 'Vinpearl Golf & Stay Hải Phòng', 'combo', 15.00,
 '2026-04-01', '2026-11-30', 'Weekday', 2, 'All',
 'Combo golf: giảm 15% giá phòng + 1 vòng golf 18 lỗ/ngày/khách. Áp dụng các ngày trong tuần (Thứ 2–Thứ 6).',
 'https://vinpearl.com/vi/khuyen-mai/golf-stay-hai-phong',
 1, '2026-06-01 08:00:00');

-- ------------------------------------------------------------
-- 5. ATTRACTION (22 điểm tham quan — phân theo destination)
-- ------------------------------------------------------------
INSERT INTO Attraction (destination_id, attraction_name, category, suitable_for, suitable_budget, suitable_preference, open_time, close_time, open_days, duration_hours, entry_fee_adult, entry_fee_child, entry_fee_note, location_area, notes, source_url) VALUES
-- Phú Quốc (dest 1) — 6 điểm
(1, 'VinWonders Phú Quốc',       'Theme Park',   'Gia đình, Cặp đôi, Nhóm bạn',  'all',    'vui_chơi',
 '09:00:00','21:00:00','All',    8.0, 650000.00, 450000.00,
 'Miễn phí cho trẻ dưới 1m. Khách lưu trú Vinpearl được ưu đãi giá đặc biệt.',
 'Bãi Dài', 'Công viên giải trí đẳng cấp quốc tế với hơn 100 trò chơi, cáp treo, sóng nhân tạo.',
 'https://vinwonders.com/vi/phu-quoc'),
(1, 'Vinpearl Safari Phú Quốc',  'Safari',       'Gia đình, Cặp đôi',             'all',    'thiên_nhiên',
 '09:00:00','16:00:00','All',    5.0, 500000.00, 350000.00,
 'Miễn phí cho trẻ dưới 3 tuổi. Vé bao gồm xe Safari tự lái khu bán hoang dã.',
 'Khu Safari', 'Vườn thú mở lớn nhất Đông Nam Á với hơn 3.000 động vật 150 loài.',
 'https://vinpearl.com/vi/safari-phu-quoc'),
(1, 'Cáp Treo Hòn Thơm',        'Nature',       'Tất cả',                         'all',    'thiên_nhiên',
 '08:00:00','17:30:00','All',    3.0, 600000.00, 400000.00,
 'Vé khứ hồi. Trẻ dưới 1m miễn phí.',
 'An Thới', 'Tuyến cáp treo 3 dây dài nhất thế giới (7.899m) vượt biển ra đảo Hòn Thơm.',
 'https://sunworld.vn/vi/hon-thom'),
(1, 'Chợ Đêm Phú Quốc',         'Night Market', 'Tất cả',                         'all',    'ẩm_thực',
 '18:00:00','23:00:00','All',    2.0, 0.00, 0.00,
 'Vào cửa miễn phí. Chi phí tùy thuộc mua sắm và ăn uống.',
 'Dương Đông', 'Chợ đêm lớn nhất Phú Quốc với hơn 150 gian hàng hải sản tươi và đồ lưu niệm.',
 'https://vinpearl.com/vi/kham-pha/cho-dem-phu-quoc'),
(1, 'Bãi Sao Phú Quốc',         'Beach',        'Tất cả',                         'all',    'biển',
 '06:00:00','18:00:00','All',    3.0, 0.00, 0.00,
 'Bãi biển công cộng, miễn phí. Dịch vụ thuê ghế ~50.000 VND/ghế.',
 'An Thới', 'Bãi biển đẹp nhất Phú Quốc với cát trắng mịn, nước trong xanh như ngọc bích.',
 'https://vinpearl.com/vi/kham-pha/bai-sao'),
(1, 'Spa & Wellness Vinpearl PQ','Spa',          'Cặp đôi, Solo',                  'luxury', 'biển',
 '09:00:00','21:00:00','All',    2.0, 500000.00, 0.00,
 'Khách lưu trú Vinpearl được giảm 20%. Đặt lịch trước tối thiểu 2 giờ.',
 'Trong resort', 'Trung tâm Spa 5 sao với massage đá nóng, liệu pháp biển và phòng xông hơi thảo mộc.',
 'https://vinpearl.com/vi/resort-spa-phu-quoc/spa'),

-- Nha Trang (dest 2) — 5 điểm
(2, 'VinWonders Nha Trang',      'Theme Park',   'Gia đình, Cặp đôi, Nhóm bạn',  'all',    'vui_chơi',
 '09:00:00','21:00:00','All',    8.0, 650000.00, 450000.00,
 'Miễn phí cho trẻ dưới 1m. Khách lưu trú Vinpearl Nha Trang được vào miễn phí.',
 'Đảo Hòn Tre', 'Công viên giải trí lớn nhất Nha Trang kết hợp sóng biển nhân tạo và công viên nước.',
 'https://vinwonders.com/vi/nha-trang'),
(2, 'Tắm Bùn Khoáng I-Resort',  'Spa',          'Tất cả',                         'all',    'thiên_nhiên',
 '07:30:00','18:00:00','All',    3.0, 250000.00, 150000.00,
 'Vé bao gồm bồn bùn cá nhân, hồ khoáng nóng lạnh và bữa ăn nhẹ.',
 'Nha Trang', 'Khu nghỉ dưỡng bùn khoáng nổi tiếng nhất Nha Trang với nguồn nước khoáng thiên nhiên.',
 'https://i-resort.com.vn'),
(2, 'Làng Chài Đêm Nha Trang',  'Dining',       'Tất cả',                         'all',    'ẩm_thực',
 '17:00:00','22:30:00','All',    2.5, 0.00, 0.00,
 'Vào cửa miễn phí. Ăn hải sản tươi theo kg — giá thị trường.',
 'Bờ biển Nha Trang', 'Phố hải sản sầm uất bên bờ biển với tôm hùm, cua Huỳnh Đế, ghẹ tươi sống.',
 'https://vinpearl.com/vi/kham-pha/lang-chai-dem-nha-trang'),
(2, 'Lặn Ngắm San Hô Hòn Mun',  'Nature',       'Cặp đôi, Nhóm bạn, Solo',       'all',    'thiên_nhiên',
 '08:00:00','15:00:00','All',    4.0, 300000.00, 200000.00,
 'Vé bao gồm thiết bị lặn snorkeling và hướng dẫn viên. Trẻ dưới 6 tuổi không tham gia.',
 'Hòn Mun', 'Khu bảo tồn biển Hòn Mun — hệ sinh thái san hô phong phú nhất vịnh Nha Trang.',
 'https://vinpearl.com/vi/kham-pha/lan-bien-hon-mun'),
(2, 'Bãi Biển Vinpearl Nha Trang','Beach',       'Tất cả',                         'all',    'biển',
 '06:00:00','18:00:00','All',    3.0, 0.00, 0.00,
 'Bãi biển riêng cho khách lưu trú Vinpearl. Khách ngoài mua vé 100.000 VND/người.',
 'Đảo Hòn Tre', 'Bãi biển cát vàng dài 700m riêng tư, nước trong và sóng nhẹ phù hợp bơi lội.',
 'https://vinpearl.com/vi/resort-spa-nha-trang/bai-bien'),

-- Nam Hội An (dest 3) — 4 điểm
(3, 'Phố Cổ Hội An',             'Cultural',     'Tất cả',                         'all',    'ẩm_thực',
 '08:00:00','22:00:00','All',    3.0, 120000.00, 60000.00,
 'Vé tham quan 5 điểm (chùa Cầu, nhà cổ, bảo tàng...). Trẻ dưới 7 tuổi miễn phí.',
 'Hội An', 'Di sản văn hóa thế giới UNESCO — phố cổ đèn lồng rực rỡ sắc màu về đêm.',
 'https://hoianworldheritage.org.vn'),
(3, 'Làng Rau Trà Quế',          'Cultural',     'Gia đình, Cặp đôi, Nhóm bạn',  'all',    'thiên_nhiên',
 '07:00:00','17:00:00','All',    2.0, 50000.00, 0.00,
 'Trẻ em miễn phí. Bao gồm trải nghiệm trồng rau cùng nông dân.',
 'Hội An', 'Làng rau sạch 400 năm tuổi — trải nghiệm nông nghiệp hữu cơ truyền thống Hội An.',
 'https://vinpearl.com/vi/kham-pha/lang-rau-tra-que'),
(3, 'Bãi An Bàng',               'Beach',        'Tất cả',                         'all',    'biển',
 '06:00:00','18:00:00','All',    3.0, 0.00, 0.00,
 'Bãi biển công cộng, miễn phí. Thuê dù và ghế ~80.000 VND.',
 'An Bàng, Hội An', 'Top 25 bãi biển đẹp nhất châu Á — cát trắng mịn, nước xanh trong, nhà hàng seafood ngay bờ biển.',
 'https://vinpearl.com/vi/kham-pha/bai-an-bang'),
(3, 'VinWonders Nam Hội An',     'Theme Park',   'Gia đình, Cặp đôi, Nhóm bạn',  'all',    'vui_chơi',
 '09:00:00','21:00:00','All',    7.0, 500000.00, 350000.00,
 'Khách lưu trú Vinpearl Nam Hội An được vào miễn phí 1 lần/ngày.',
 'Nam Hội An', 'Công viên giải trí chủ đề văn hóa Hội An và thế giới với 5 khu vực trải nghiệm.',
 'https://vinwonders.com/vi/nam-hoi-an'),

-- Cửa Hội (dest 4) — 3 điểm
(4, 'Bãi Biển Cửa Lò',          'Beach',        'Tất cả',                         'all',    'biển',
 '05:30:00','19:00:00','All',    3.0, 0.00, 0.00,
 'Miễn phí. Bãi biển rộng lớn, sạch, nhiều dịch vụ thể thao nước.',
 'Cửa Lò', 'Bãi biển nổi tiếng miền Trung với cát vàng mịn, sóng vừa phải, thuận lợi cho gia đình.',
 'https://vinpearl.com/vi/kham-pha/bai-cua-lo'),
(4, 'Chợ Hải Sản Cửa Hội',      'Dining',       'Tất cả',                         'all',    'ẩm_thực',
 '04:30:00','11:00:00','All',    1.5, 0.00, 0.00,
 'Miễn phí vào chợ. Nên đến sớm trước 6h để chọn hải sản tươi nhất.',
 'Cửa Hội', 'Chợ đầu mối hải sản tươi sống lớn nhất Nghệ An — cá, tôm, mực, ghẹ giá rẻ tại nguồn.',
 'https://vinpearl.com/vi/kham-pha/cho-hai-san-cua-hoi'),
(4, 'Đảo Ngư Cửa Hội',          'Nature',       'Tất cả',                         'all',    'thiên_nhiên',
 '08:00:00','16:00:00','All',    4.0, 150000.00, 80000.00,
 'Vé tàu khứ hồi. Trẻ dưới 5 tuổi miễn phí.',
 'Ngoài khơi Cửa Hội', 'Đảo nhỏ hoang sơ cách bờ 5km — lý tưởng câu cá, picnic và tắm biển trong xanh.',
 'https://vinpearl.com/vi/kham-pha/dao-ngu'),

-- Hải Phòng (dest 5) — 4 điểm
(5, 'Đảo Cát Bà',               'Nature',       'Tất cả',                         'all',    'thiên_nhiên',
 '07:00:00','17:00:00','All',    6.0, 100000.00, 50000.00,
 'Vé phà/tàu cao tốc mua riêng (~200.000 VND khứ hồi). Phí vườn quốc gia 100.000 VND.',
 'Cát Bà', 'Đảo lớn nhất quần đảo Cát Bà — vườn quốc gia, leo núi, kayak và vịnh Lan Hạ tuyệt đẹp.',
 'https://vinpearl.com/vi/kham-pha/dao-cat-ba'),
(5, 'Bãi Đồ Sơn',               'Beach',        'Tất cả',                         'all',    'biển',
 '06:00:00','18:00:00','All',    3.0, 0.00, 0.00,
 'Miễn phí. Thuê phòng thay đồ và ghế nằm khoảng 30.000-50.000 VND.',
 'Đồ Sơn', 'Bán đảo biển nổi tiếng Hải Phòng — sóng vừa, bãi cát rộng, gần resort Vinpearl.',
 'https://vinpearl.com/vi/kham-pha/bai-do-son'),
(5, 'Sân Golf Vinpearl Hải Phòng','Entertainment','Cặp đôi, Nhóm bạn, Solo',      'luxury', 'vui_chơi',
 '06:00:00','18:00:00','All',    5.0, 1500000.00, 0.00,
 'Vé 18 lỗ. Thuê gậy 200.000 VND. Khách lưu trú Golf Package được giảm theo ưu đãi.',
 'Đảo Vũ Yên', 'Sân golf 18 lỗ championship view biển — một trong những sân golf đẹp nhất miền Bắc.',
 'https://vinpearl.com/vi/hai-phong/golf'),
(5, 'Nhà Hàng Hải Sản Đồ Sơn',  'Dining',       'Tất cả',                         'all',    'ẩm_thực',
 '10:00:00','22:00:00','All',    2.0, 0.00, 0.00,
 'Chi phí ăn uống theo order — trung bình 200.000-500.000 VND/người.',
 'Đồ Sơn', 'Phố nhà hàng hải sản tươi sống ngay bờ biển Đồ Sơn — cua, tôm, bào ngư chế biến tại chỗ.',
 'https://vinpearl.com/vi/kham-pha/hai-san-do-son');

-- ------------------------------------------------------------
-- 6. TRAVEL_MATRIX (di chuyển trong từng điểm đến)
-- ------------------------------------------------------------
INSERT INTO Travel_Matrix (destination_id, from_location, to_location, transport_type, duration_minutes, distance_km, cost_estimate_vnd, notes) VALUES
-- Phú Quốc (dest 1)
(1, 'Vinpearl Resort PQ',        'VinWonders Phú Quốc',    'Xe điện resort',  15, 3.5,       0, 'Xe điện miễn phí cho khách lưu trú'),
(1, 'Vinpearl Resort PQ',        'Vinpearl Safari',         'Xe điện resort',  10, 2.0,       0, 'Xe điện miễn phí cho khách lưu trú'),
(1, 'Vinpearl Resort PQ',        'Cáp Treo Hòn Thơm',      'Taxi',            25, 18.0,  80000, 'Taxi/Grab từ Bãi Dài xuống An Thới'),
(1, 'Vinpearl Resort PQ',        'Chợ Đêm Phú Quốc',       'Taxi',            30, 22.0, 100000, 'Taxi từ Bãi Dài về Dương Đông'),
(1, 'Vinpearl Resort PQ',        'Bãi Sao Phú Quốc',       'Taxi',            35, 25.0, 110000, 'Taxi xuống cuối đảo phía Nam'),
(1, 'Vinpearl Resort PQ',        'Spa & Wellness Vinpearl', 'Đi bộ',           5, 0.3,       0, 'Đi bộ trong khuôn viên resort'),
(1, 'VinWonders Phú Quốc',       'Vinpearl Safari',         'Xe điện resort',   5, 1.0,       0, 'Hai khu liền kề nhau'),
(1, 'Vinpearl Safari',           'Chợ Đêm Phú Quốc',       'Taxi',            35, 24.0, 100000, 'Taxi từ khu Safari về Dương Đông'),
(1, 'Bãi Sao Phú Quốc',         'Cáp Treo Hòn Thơm',      'Đi bộ',           10, 0.8,       0, 'Cách nhau khoảng 1km, đi bộ hoặc xe điện'),
-- Nha Trang (dest 2)
(2, 'Vinpearl Resort NT',        'VinWonders Nha Trang',    'Cáp treo',        15, 3.2,       0, 'Cáp treo miễn phí cho khách lưu trú'),
(2, 'Vinpearl Resort NT',        'Tắm Bùn Khoáng I-Resort', 'Taxi',            20, 10.0,  60000, 'Taxi từ bến tàu vào đất liền'),
(2, 'Vinpearl Resort NT',        'Làng Chài Đêm Nha Trang', 'Taxi',            15,  7.0,  50000, 'Taxi hoặc xe ôm'),
(2, 'Vinpearl Resort NT',        'Lặn Ngắm San Hô Hòn Mun', 'Tàu',            30,  8.0, 150000, 'Tàu tour từ cầu cảng Vinpearl'),
(2, 'Vinpearl Resort NT',        'Bãi Biển Vinpearl NT',    'Đi bộ',            3, 0.2,       0, 'Bãi biển nằm trong khuôn viên resort'),
(2, 'VinWonders Nha Trang',      'Làng Chài Đêm Nha Trang', 'Taxi',            20, 10.0,  60000, 'Từ bến cáp treo đất liền đi taxi'),
-- Nam Hội An (dest 3)
(3, 'Vinpearl Nam Hội An',       'Phố Cổ Hội An',           'Taxi',            35, 30.0, 150000, 'Taxi hoặc xe điện tour từ resort'),
(3, 'Vinpearl Nam Hội An',       'Làng Rau Trà Quế',        'Taxi',            30, 26.0, 130000, 'Taxi hoặc xe máy thuê'),
(3, 'Vinpearl Nam Hội An',       'Bãi An Bàng',             'Xe điện resort',  10, 2.5,       0, 'Xe điện miễn phí trong khuôn viên resort'),
(3, 'Vinpearl Nam Hội An',       'VinWonders Nam Hội An',   'Đi bộ',            5, 0.3,       0, 'VinWonders nằm trong khu resort'),
(3, 'Phố Cổ Hội An',             'Bãi An Bàng',             'Xe đạp',          20, 4.0,  30000, 'Thuê xe đạp tại phố cổ ~30.000 VND/ngày'),
-- Cửa Hội (dest 4)
(4, 'Vinpearl Cửa Hội',          'Bãi Biển Cửa Lò',         'Đi bộ',            5, 0.3,       0, 'Bãi biển sát resort'),
(4, 'Vinpearl Cửa Hội',          'Chợ Hải Sản Cửa Hội',    'Taxi',            15, 5.0,  40000, 'Taxi ra chợ sớm buổi sáng'),
(4, 'Vinpearl Cửa Hội',          'Đảo Ngư Cửa Hội',         'Tàu',            45, 7.0, 150000, 'Tàu du lịch từ bến cảng Cửa Hội'),
(4, 'Chợ Hải Sản Cửa Hội',       'Bãi Biển Cửa Lò',         'Taxi',            15, 4.5,  40000, NULL),
-- Hải Phòng (dest 5)
(5, 'Vinpearl Resort HP',        'Đảo Cát Bà',              'Tàu cao tốc',     60, 25.0, 250000, 'Tàu cao tốc từ cảng Đình Vũ'),
(5, 'Vinpearl Resort HP',        'Bãi Đồ Sơn',              'Xe điện resort',  15, 4.0,       0, 'Xe điện resort miễn phí'),
(5, 'Vinpearl Resort HP',        'Sân Golf Vinpearl HP',    'Đi bộ',            5, 0.4,       0, 'Sân golf nằm trong khuôn viên resort'),
(5, 'Vinpearl Resort HP',        'Nhà Hàng Hải Sản Đồ Sơn', 'Taxi',            20, 5.0,  50000, 'Taxi hoặc xe điện resort'),
(5, 'Bãi Đồ Sơn',               'Nhà Hàng Hải Sản Đồ Sơn', 'Đi bộ',           5, 0.5,       0, 'Nhà hàng sát bãi biển Đồ Sơn');

-- ------------------------------------------------------------
-- 7. USER_SESSION (5 phiên hội thoại)
-- ------------------------------------------------------------
INSERT INTO User_Session (session_token, started_at, completed_at, status) VALUES
('TOK-A1B2C3-001', '2026-06-01 09:15:00', '2026-06-01 09:28:00', 'completed'),
('TOK-D4E5F6-002', '2026-06-02 14:30:00', '2026-06-02 14:47:00', 'completed'),
('TOK-G7H8I9-003', '2026-06-03 10:05:00', '2026-06-03 10:19:00', 'completed'),
('TOK-J1K2L3-004', '2026-06-04 08:40:00', NULL,                  'in_progress'),
('TOK-M4N5O6-005', '2026-06-04 11:20:00', '2026-06-04 11:33:00', 'completed');

-- ------------------------------------------------------------
-- 8. USER_INPUT (input của 5 session)
-- ------------------------------------------------------------
INSERT INTO User_Input (session_id, destination_id, travel_group, num_adults, num_children, children_ages, budget_level, budget_per_night, preference, checkin_date, checkout_date, is_clarified) VALUES
-- Session 1: Cặp đôi luxury, Phú Quốc, biển, hè 2026
(1, 1, 'couple', 2, 0, NULL, 'luxury', 7000000.00, 'beach',
 '2026-07-15', '2026-07-17', 0),
-- Session 2: Gia đình có trẻ nhỏ, Nha Trang, mid, giải trí
(2, 2, 'family_kids', 2, 2, '5,8', 'mid', 4000000.00, 'entertainment',
 '2026-08-01', '2026-08-03', 0),
-- Session 3: Solo, Phú Quốc, mid, thiên nhiên
(3, 1, 'solo', 1, 0, NULL, 'mid', 2500000.00, 'nature',
 '2026-06-20', '2026-06-22', 0),
-- Session 4: Nhóm bạn, Nam Hội An, mid, mix (đang trong luồng hỏi)
(4, 3, 'group_friends', 4, 0, NULL, 'mid', 3000000.00, 'mix',
 '2026-09-05', '2026-09-07', 1, 'preference',
 'Bạn muốn ưu tiên trải nghiệm nào hơn: khám phá phố cổ Hội An hay thư giãn biển An Bàng?',
 NULL),
-- Session 5: Cặp đôi luxury, Hải Phòng, thiên nhiên/golf
(5, 5, 'couple', 2, 0, NULL, 'luxury', 4500000.00, 'nature',
 '2026-10-10', '2026-10-12', 0);

-- ------------------------------------------------------------
-- 9. ITINERARY (4 lịch trình đã sinh — session 4 chưa xong)
-- ------------------------------------------------------------
INSERT INTO Itinerary (session_id, destination_id, generated_at, room_type_id, room_reason, promotion_id, promotion_reason, no_promotion_reason, estimated_cost_min, estimated_cost_max, confidence_score, status) VALUES
-- Itinerary 1: Session 1 — Cặp đôi luxury Phú Quốc, biển
(1, 1, '2026-06-01 09:28:00',
 3,  -- Beachfront Pool Villa PQ (luxury, resort 1, view biển)
 'Khách đi cặp đôi, ngân sách luxury (7tr/đêm), sở thích biển — Pool Villa hướng biển tại VPR_PQ là lựa chọn tối ưu: hồ bơi riêng, bãi biển 30m, view hoàng hôn tuyệt đẹp.',
 1,  -- Hè Vàng Phú Quốc 20%
 'Chương trình Hè Vàng Phú Quốc 2026 đang áp dụng, giảm 20% cho lưu trú từ 2 đêm trong tháng 7. Khách tiết kiệm được 2.880.000 VND.',
 NULL,
 11520000.00, 15000000.00, 95, 'accepted'),

-- Itinerary 2: Session 2 — Gia đình mid Nha Trang, giải trí
(2, 2, '2026-06-02 14:47:00',
 11,  -- Family Deluxe NT (mid, resort 5, 2A+2C)
 'Gia đình 2 người lớn + 2 trẻ (5 và 8 tuổi), ngân sách mid — Family Deluxe NT đủ sức chứa, bao gồm bữa sáng, giá 3.800.000 VND/đêm phù hợp ngân sách 4tr/đêm.',
 4,  -- Early Bird 10%
 'Khách đặt trước hơn 30 ngày so với ngày check-in (2026-08-01), đủ điều kiện Early Bird giảm 10%. Tiết kiệm 760.000 VND/đêm.',
 NULL,
 6840000.00, 9500000.00, 92, 'accepted'),

-- Itinerary 3: Session 3 — Solo mid Phú Quốc, thiên nhiên
(3, 1, '2026-06-03 10:19:00',
 4,  -- Discovery Deluxe Bungalow (mid, resort 2)
 'Khách solo, ngân sách mid (2.500.000/đêm), thích thiên nhiên — Discovery Deluxe Bungalow tại VPD1_PQ lý tưởng: bungalow gần biển, không khí hoang sơ, phù hợp khám phá một mình.',
 4,  -- Early Bird 10%
 'Khách đặt trước 17 ngày (check-in 20/6, đặt 3/6), đủ điều kiện Early Bird 10%. Tiết kiệm 250.000 VND/đêm.',
 NULL,
 4500000.00, 6500000.00, 88, 'accepted'),

-- Itinerary 4: Session 5 — Cặp đôi luxury Hải Phòng, thiên nhiên/golf
(5, 5, '2026-06-04 11:33:00',
 21,  -- Ocean Suite HP (luxury, resort 9)
 'Cặp đôi luxury, thích thiên nhiên tại Hải Phòng — Ocean Suite view biển tại Vinpearl HP kết hợp hoàn hảo với golf và tour Cát Bà. Phòng 65m², ban công hướng biển.',
 8,  -- Golf & Stay HP Package (15% weekday)
 'Chương trình Golf & Stay đang áp dụng ngày trong tuần (10-11/10 là Thứ 7-CN — KHÔNG áp dụng). Tuy nhiên khách check-in Thứ 7 nên không hưởng ưu đãi này.',
 'Check-in ngày 10/10/2026 (Thứ 7) — chương trình Golf & Stay chỉ áp dụng Weekday (Thứ 2-Thứ 6). Hiện chưa có ưu đãi nào phù hợp với lịch trình này. Đề xuất điều chỉnh ngày sang Thứ 2-Thứ 4 để hưởng ưu đãi 15%.',
 8100000.00, 11000000.00, 78, 'modified');

-- ------------------------------------------------------------
-- 10. ITINERARY_TIMELINE (lịch trình chi tiết 2N1Đ)
-- ------------------------------------------------------------

-- === ITINERARY 1: Cặp đôi luxury Phú Quốc ===
INSERT INTO Itinerary_Timeline (itinerary_id, day_number, time_slot, start_time, end_time, attraction_id, activity_note, ai_reason, travel_to_next_min, order_in_day) VALUES
-- Ngày 1
(1, 1, 'morning',   '07:00:00', '10:00:00',  5,
 'Đón bình minh tại Bãi Sao — bãi biển đẹp nhất Phú Quốc. Tắm biển, chụp ảnh, thư giãn.',
 'Buổi sáng sớm Bãi Sao ít người, ánh sáng đẹp cho ảnh. Phù hợp cặp đôi muốn không gian riêng tư lãng mạn.',
 30, 1),
(1, 1, 'afternoon', '11:00:00', '17:30:00',  1,
 'Khám phá VinWonders Phú Quốc — thế giới giải trí đa sắc màu. Ưu tiên sóng nhân tạo và tàu lượn siêu tốc.',
 'VinWonders cần 6-7 tiếng để trải nghiệm đầy đủ. Buổi chiều ít đông hơn sáng. Phù hợp sau buổi sáng thư giãn biển.',
 25, 2),
(1, 1, 'evening',   '19:00:00', '21:30:00',  4,
 'Dạo Chợ Đêm Phú Quốc — thưởng thức hải sản tươi sống và mua sắm đồ lưu niệm.',
 'Chợ Đêm Dương Đông là điểm đến buổi tối không thể bỏ qua ở Phú Quốc. Không khí sôi động, hải sản tươi ngon.',
 0, 3),
-- Ngày 2
(1, 2, 'morning',   '08:30:00', '13:00:00',  2,
 'Safari Vinpearl — gặp gỡ hơn 3.000 động vật trong môi trường bán hoang dã. Xe Safari tự lái khu Open Safari.',
 'Safari mở cửa 9h nhưng đến 8:30 để mua vé tránh xếp hàng. Buổi sáng động vật hoạt động nhiều hơn buổi chiều.',
 20, 1),
(1, 2, 'afternoon', '14:00:00', '17:00:00',  3,
 'Trải nghiệm Cáp Treo Hòn Thơm — 7.899m vượt biển, view đảo và biển Tây hùng vĩ.',
 'Chiều nắng vàng làm màu biển đẹp hơn buổi sáng. Đây là cáp treo dài nhất thế giới — điểm check-in không thể bỏ qua.',
 20, 2),
(1, 2, 'evening',   '18:30:00', '20:30:00',  6,
 'Spa & Wellness Vinpearl — massage đá nóng 90 phút, thư giãn trước khi kết thúc chuyến đi.',
 'Sau ngày dài khám phá, liệu pháp Spa trong resort giúp phục hồi và thư giãn tối đa. Phù hợp cặp đôi muốn kết thúc chuyến đi nhẹ nhàng.',
 0, 3),

-- === ITINERARY 2: Gia đình Nha Trang ===
(2, 1, 'morning',   '08:30:00', '17:00:00',  7,
 'Cả ngày tại VinWonders Nha Trang — công viên nước, sóng nhân tạo, tàu lượn dành cho mọi lứa tuổi.',
 'VinWonders NT có khu riêng cho trẻ em 5-8 tuổi (độ tuổi phù hợp). Cần cả ngày để trải nghiệm đầy đủ. Đây là lý do chính khách chọn Nha Trang.',
 15, 1),
(2, 1, 'evening',   '17:30:00', '20:00:00',  9,
 'Dùng bữa tối tại Làng Chài Đêm — hải sản tươi sống ngay bờ biển.',
 'Sau ngày dài vui chơi, gia đình cần bữa tối đặc trưng địa phương. Làng Chài Đêm sôi động, trẻ em thích thú.',
 0, 2),
-- Ngày 2
(2, 2, 'morning',   '09:00:00', '12:00:00',  8,
 'Tắm Bùn Khoáng I-Resort — trải nghiệm thư giãn đặc biệt cho cả gia đình.',
 'Tắm bùn an toàn cho trẻ từ 5 tuổi trở lên. Buổi sáng ít đông hơn, nhiệt độ dễ chịu hơn.',
 30, 1),
(2, 2, 'afternoon', '13:30:00', '17:00:00', 11,
 'Thư giãn tại Bãi Biển Vinpearl — bãi biển riêng tư, nước trong, sóng nhẹ phù hợp cho trẻ nhỏ.',
 'Sau buổi sáng tắm bùn, chiều tắm biển là lựa chọn hoàn hảo. Bãi biển riêng của Vinpearl an toàn và sạch sẽ cho trẻ em.',
 0, 2),

-- === ITINERARY 3: Solo Phú Quốc, thiên nhiên ===
(3, 1, 'morning',   '08:00:00', '13:00:00',  2,
 'Safari một mình — quan sát động vật, chụp ảnh wildlife không bị phân tâm.',
 'Solo traveler sẽ tập trung quan sát và chụp ảnh tốt hơn khi đi một mình. Buổi sáng động vật hoạt động nhiều nhất.',
 20, 1),
(3, 1, 'afternoon', '14:00:00', '17:30:00',  3,
 'Cáp Treo Hòn Thơm — khám phá đảo nhỏ, tắm biển hoang sơ tại Hòn Thơm.',
 'Từ Safari di chuyển xuống An Thới khá gần. Đảo Hòn Thơm phù hợp du lịch solo — có thể tự khám phá theo ý thích.',
 25, 2),
(3, 1, 'evening',   '19:00:00', '21:00:00',  4,
 'Chợ Đêm Phú Quốc — ăn tối hải sản, quan sát văn hóa địa phương.',
 'Solo traveler dễ hòa nhập tại Chợ Đêm, dễ tìm chỗ ngồi ở quán nhỏ, trải nghiệm ẩm thực đặc trưng.',
 0, 3),
-- Ngày 2
(3, 2, 'morning',   '07:00:00', '10:30:00',  5,
 'Bãi Sao lúc bình minh — tắm biển, đọc sách, thư giãn hoàn toàn.',
 'Buổi sáng sớm Bãi Sao gần như không có người — thiên đường cho solo traveler muốn yên tĩnh và kết nối với thiên nhiên.',
 30, 1),
(3, 2, 'afternoon', '12:00:00', '17:00:00',  1,
 'VinWonders Phú Quốc buổi chiều — vào sau 12h được giảm giá vé, tập trung khu outdoor.',
 'Chiều tà VinWonders ít đông hơn buổi sáng. Solo nên vào chiều, tránh đám đông, tập trung các trò ngoài trời.',
 0, 2),

-- === ITINERARY 4: Cặp đôi luxury Hải Phòng ===
(4, 1, 'morning',   '08:00:00', '15:00:00', 19,
 'Tour Đảo Cát Bà — tàu cao tốc, kayak trong vịnh Lan Hạ, leo núi ngắm view.',
 'Cát Bà là điểm đến thiên nhiên đặc trưng nhất Hải Phòng. Khởi hành sớm để có đủ thời gian khám phá — vịnh Lan Hạ đẹp hơn cả Hạ Long vào mùa thu.',
 20, 1),
(4, 1, 'evening',   '18:00:00', '20:30:00', 22,
 'Tối đầu tiên thưởng thức hải sản tươi Đồ Sơn — cua, tôm hùm, sò điệp ngay bờ biển.',
 'Sau ngày dài trên biển, nhà hàng hải sản Đồ Sơn là lựa chọn hoàn hảo — nguyên liệu cực tươi, không khí lãng mạn.',
 0, 2),
-- Ngày 2
(4, 2, 'morning',   '07:00:00', '10:00:00', 20,
 'Đón bình minh tại Bãi Đồ Sơn — tắm biển, đi bộ dọc bờ biển.',
 'Bãi Đồ Sơn ngay cạnh resort — đi bộ 5 phút. Bình minh tháng 10 tại Hải Phòng rất đẹp.',
 5, 1),
(4, 2, 'morning',   '10:30:00', '15:30:00', 21,
 'Sân Golf Vinpearl 18 lỗ — trải nghiệm golf view biển đẳng cấp championship.',
 'Golf là lý do chính khách chọn Vinpearl Hải Phòng. Buổi sáng thời tiết tốt nhất để chơi golf tháng 10.',
 0, 2);

-- ------------------------------------------------------------
-- 11. USER_CORRECTION (chỉnh sửa lịch trình)
-- ------------------------------------------------------------
INSERT INTO User_Correction (session_id, itinerary_id, correction_type, old_value, new_value, corrected_at, new_itinerary_id) VALUES
-- Session 2 ban đầu chọn 'luxury' nhưng sau đó sửa lại 'mid'
(2, 2, 'change_budget',
 'budget_level=luxury, budget_per_night=6000000',
 'budget_level=mid, budget_per_night=4000000',
 '2026-06-02 14:40:00', NULL),
-- Session 5 yêu cầu đổi ngày để hưởng ưu đãi Golf Package
(5, 4, 'change_date',
 'checkin_date=2026-10-10, checkout_date=2026-10-12',
 'checkin_date=2026-10-13, checkout_date=2026-10-15',
 '2026-06-04 11:40:00', NULL);

-- ------------------------------------------------------------
-- 12. USER_FEEDBACK (đánh giá sau khi nhận lịch trình)
-- ------------------------------------------------------------
INSERT INTO User_Feedback (session_id, itinerary_id, rating, found_useful, promotion_accurate, comment, submitted_at) VALUES
(1, 1, 5, 1, 1,
 'Lịch trình rất chi tiết và phù hợp! Đặc biệt thích gợi ý Pool Villa view biển và ưu đãi Hè Vàng 20%. Sẽ đặt ngay hôm nay.',
 '2026-06-01 09:35:00'),
(2, 2, 4, 1, 1,
 'Lịch trình phù hợp cho gia đình. Gợi ý VinWonders nguyên ngày là đúng vì có 2 bé nhỏ. Thông tin Early Bird chính xác.',
 '2026-06-02 14:55:00'),
(3, 3, 4, 1, NULL,
 'Tốt! Lịch trình solo thiên nhiên rất hợp với mình. Chỉ muốn thêm 1 hoạt động lặn biển nếu có thể.',
 '2026-06-03 10:30:00'),
(5, 4, 3, 1, 0,
 'Lịch trình OK nhưng AI cần check kỹ hơn — ưu đãi Golf Package không áp dụng cuối tuần mà tôi check-in. May AI có giải thích rõ, không bị nhầm.',
 '2026-06-04 11:45:00');

-- ------------------------------------------------------------
-- 13. AI_DECISION_LOG (audit trail — không hallucinate)
-- ------------------------------------------------------------
INSERT INTO AI_Decision_Log (session_id, decision_type, input_context, output_decision, data_source_ids, is_hallucination, confidence, logged_at) VALUES
-- Session 1: chọn phòng
(1, 'room_selection',
 '{"destination_id":1,"travel_group":"couple","budget_level":"luxury","preference":"beach","num_adults":2,"num_children":0}',
 '{"selected_room_type_id":3,"room_name":"Beachfront Pool Villa Phú Quốc","resort_id":1,"resort_name":"Vinpearl Resort & Spa Phú Quốc","price_per_night":7200000,"reason":"Cặp đôi luxury + sở thích biển → Pool Villa hướng biển tối ưu"}',
 'room_type_id=3, resort_id=1', 0, 95, '2026-06-01 09:27:00'),
-- Session 1: chọn promotion
(1, 'promotion_selection',
 '{"destination_id":1,"checkin_date":"2026-07-15","checkout_date":"2026-07-17","min_nights":2}',
 '{"selected_promotion_id":1,"promotion_name":"Hè Vàng Phú Quốc 2026","discount_type":"percentage","discount_value":20,"saving_vnd":2880000}',
 'promotion_id=1', 0, 95, '2026-06-01 09:27:30'),
-- Session 1: gắn timeline Ngày 1 sáng
(1, 'timeline_slot',
 '{"day":1,"slot":"morning","preference":"beach","travel_group":"couple"}',
 '{"attraction_id":5,"attraction_name":"Bãi Sao Phú Quốc","start":"07:00","end":"10:00","reason":"Bình minh ít người, ánh sáng đẹp, phù hợp cặp đôi"}',
 'attraction_id=5, matrix_id=5', 0, 90, '2026-06-01 09:27:45'),
-- Session 2: chọn phòng
(2, 'room_selection',
 '{"destination_id":2,"travel_group":"family_kids","budget_level":"mid","num_adults":2,"num_children":2,"children_ages":"5,8"}',
 '{"selected_room_type_id":11,"room_name":"Family Deluxe Nha Trang","resort_id":5,"price_per_night":3800000,"reason":"capacity_children=2 đủ cho 2 bé, giá trong ngân sách 4tr/đêm"}',
 'room_type_id=11, resort_id=5', 0, 92, '2026-06-02 14:46:00'),
-- Session 2: chọn promotion
(2, 'promotion_selection',
 '{"destination_id":2,"checkin_date":"2026-08-01","booking_date":"2026-06-02","days_in_advance":60}',
 '{"selected_promotion_id":4,"promotion_name":"Early Bird Vinpearl","discount_value":10,"reason":"Đặt trước 60 ngày > 10 ngày yêu cầu, đủ điều kiện"}',
 'promotion_id=4', 0, 92, '2026-06-02 14:46:30'),
-- Session 3: chọn phòng solo
(3, 'room_selection',
 '{"destination_id":1,"travel_group":"solo","budget_level":"mid","preference":"nature","num_adults":1,"num_children":0}',
 '{"selected_room_type_id":4,"room_name":"Discovery Deluxe Bungalow","resort_id":2,"resort_name":"Vinpearl Discovery 1 Phú Quốc","reason":"Solo + thiên nhiên → Discovery resort ven biển hoang sơ phù hợp nhất"}',
 'room_type_id=4, resort_id=2', 0, 88, '2026-06-03 10:18:00'),
-- Session 4: hỏi lại vì preference không rõ
(4, 'clarification_ask',
 '{"destination_id":3,"preference":"mix","travel_group":"group_friends"}',
 '{"clarification_field":"preference","question":"Bạn muốn ưu tiên trải nghiệm nào hơn: khám phá phố cổ Hội An hay thư giãn biển An Bàng?","reason":"mix không đủ thông tin để xếp lịch tối ưu, cần ưu tiên rõ hơn"}',
 NULL, 0, 100, '2026-06-04 08:41:00'),
-- Session 5: no_promotion_response — ưu đãi không áp dụng
(5, 'no_promotion_response',
 '{"destination_id":5,"resort_id":9,"checkin_date":"2026-10-10","day_of_week":"Saturday","applicable_promotions_found":1}',
 '{"promotion_id_checked":8,"reason_not_applied":"Promo Golf & Stay chỉ áp dụng Weekday (Mon-Fri). Check-in 10/10 là Thứ 7 — KHÔNG đủ điều kiện","recommendation":"Đổi check-in sang Thứ 2-Thứ 4 để hưởng ưu đãi 15%"}',
 'promotion_id=8', 0, 78, '2026-06-04 11:32:00'),
-- Session 5: chọn phòng
(5, 'room_selection',
 '{"destination_id":5,"travel_group":"couple","budget_level":"luxury","preference":"nature","num_adults":2,"num_children":0}',
 '{"selected_room_type_id":21,"room_name":"Ocean Suite Hải Phòng","resort_id":9,"price_per_night":4500000,"reason":"Cặp đôi luxury + thiên nhiên → Ocean Suite view biển, gần sân golf và cầu cảng Cát Bà"}',
 'room_type_id=21, resort_id=9', 0, 78, '2026-06-04 11:32:30');
