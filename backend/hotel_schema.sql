-- ============================================================
--  HOTEL MANAGEMENT SCHEMA  (PostgreSQL / SQLite compatible)
--  24 tables — auto-generated from mock_data.sql analysis
-- ============================================================

CREATE TABLE IF NOT EXISTS room_type (
    room_type_id    SERIAL PRIMARY KEY,
    type_name       TEXT    NOT NULL,
    base_price      REAL    NOT NULL,
    capacity        INTEGER NOT NULL DEFAULT 2,
    num_beds        INTEGER NOT NULL DEFAULT 1,
    bed_type        TEXT,
    area_sqm        REAL,
    floor_type      TEXT,
    description     TEXT,
    thumbnail_url   TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS room_type_amenity (
    id              SERIAL PRIMARY KEY,
    room_type_id    INTEGER NOT NULL REFERENCES room_type(room_type_id),
    amenity_name    TEXT    NOT NULL,
    amenity_icon    TEXT
);

CREATE TABLE IF NOT EXISTS department (
    department_id   SERIAL PRIMARY KEY,
    dept_name       TEXT    NOT NULL,
    dept_code       TEXT    NOT NULL UNIQUE,
    description     TEXT,
    manager_id      INTEGER,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id        SERIAL PRIMARY KEY,
    employee_code   TEXT    NOT NULL UNIQUE,
    full_name       TEXT    NOT NULL,
    email           TEXT    UNIQUE,
    phone           TEXT,
    department_id   INTEGER REFERENCES department(department_id),
    role            TEXT,
    shift           TEXT,
    hire_date       TEXT,
    salary          REAL,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS staff_account (
    account_id      SERIAL PRIMARY KEY,
    staff_id        INTEGER NOT NULL REFERENCES staff(staff_id),
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    role_level      TEXT    NOT NULL DEFAULT 'staff',
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS shift_schedule (
    schedule_id     SERIAL PRIMARY KEY,
    staff_id        INTEGER NOT NULL REFERENCES staff(staff_id),
    shift_date      TEXT    NOT NULL,
    shift_type      TEXT    NOT NULL,
    start_time      TEXT,
    end_time        TEXT,
    actual_start    TEXT,
    actual_end      TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS room_type_promotion (
    promotion_id    SERIAL PRIMARY KEY,
    room_type_id    INTEGER NOT NULL REFERENCES room_type(room_type_id),
    promotion_name  TEXT    NOT NULL,
    discount_type   TEXT    NOT NULL,
    discount_value  REAL    NOT NULL,
    min_nights      INTEGER NOT NULL DEFAULT 1,
    valid_from      TEXT    NOT NULL,
    valid_to        TEXT    NOT NULL,
    day_of_week     TEXT    NOT NULL DEFAULT 'All',
    max_uses        INTEGER,
    used_count      INTEGER NOT NULL DEFAULT 0,
    conditions      TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_by      INTEGER REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS room (
    room_id         SERIAL PRIMARY KEY,
    room_number     TEXT    NOT NULL UNIQUE,
    floor           INTEGER NOT NULL,
    room_type_id    INTEGER NOT NULL REFERENCES room_type(room_type_id),
    view_type       TEXT,
    status          TEXT    NOT NULL DEFAULT 'available',
    last_cleaned_at TEXT,
    notes           TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS room_rate (
    rate_id         SERIAL PRIMARY KEY,
    room_type_id    INTEGER NOT NULL REFERENCES room_type(room_type_id),
    rate_name       TEXT    NOT NULL,
    price           REAL    NOT NULL,
    valid_from      TEXT    NOT NULL,
    valid_to        TEXT    NOT NULL,
    day_of_week     TEXT    NOT NULL DEFAULT 'All',
    priority        INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS guest (
    guest_id            SERIAL PRIMARY KEY,
    full_name           TEXT    NOT NULL,
    email               TEXT    UNIQUE,
    phone               TEXT,
    id_number           TEXT,
    id_type             TEXT,
    id_issue_date       TEXT,
    id_expiry_date      TEXT,
    nationality         TEXT,
    date_of_birth       TEXT,
    gender              TEXT,
    address             TEXT,
    city                TEXT,
    country             TEXT,
    company_name        TEXT,
    loyalty_tier        TEXT    NOT NULL DEFAULT 'Standard',
    loyalty_points      INTEGER NOT NULL DEFAULT 0,
    total_stays         INTEGER NOT NULL DEFAULT 0,
    total_spent         REAL    NOT NULL DEFAULT 0.0,
    preferred_room_type INTEGER REFERENCES room_type(room_type_id),
    special_notes       TEXT,
    is_blacklisted      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS guest_account (
    account_id      SERIAL PRIMARY KEY,
    guest_id        INTEGER NOT NULL REFERENCES guest(guest_id),
    username        TEXT    NOT NULL UNIQUE,
    password_hash   TEXT    NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS reservation (
    reservation_id      SERIAL PRIMARY KEY,
    reservation_code    TEXT    NOT NULL UNIQUE,
    guest_id            INTEGER NOT NULL REFERENCES guest(guest_id),
    room_id             INTEGER NOT NULL REFERENCES room(room_id),
    promotion_id        INTEGER REFERENCES room_type_promotion(promotion_id),
    check_in_date       TEXT    NOT NULL,
    check_out_date      TEXT    NOT NULL,
    num_adults          INTEGER NOT NULL DEFAULT 1,
    num_children        INTEGER NOT NULL DEFAULT 0,
    room_rate           REAL    NOT NULL,
    subtotal            REAL    NOT NULL DEFAULT 0.0,
    discount_amount     REAL    NOT NULL DEFAULT 0.0,
    total_amount        REAL    NOT NULL DEFAULT 0.0,
    deposit_amount      REAL    NOT NULL DEFAULT 0.0,
    balance_due         REAL    NOT NULL DEFAULT 0.0,
    source              TEXT    NOT NULL DEFAULT 'website',
    status              TEXT    NOT NULL DEFAULT 'pending',
    special_requests    TEXT,
    confirmed_by        INTEGER REFERENCES staff(staff_id),
    cancelled_at        TEXT,
    cancel_reason       TEXT,
    created_at          TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE IF NOT EXISTS reservation_guest (
    id              SERIAL PRIMARY KEY,
    reservation_id  INTEGER NOT NULL REFERENCES reservation(reservation_id),
    full_name       TEXT    NOT NULL,
    id_number       TEXT,
    date_of_birth   TEXT,
    nationality     TEXT,
    is_primary      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS check_in_out (
    id                  SERIAL PRIMARY KEY,
    reservation_id      INTEGER NOT NULL REFERENCES reservation(reservation_id),
    actual_check_in     TEXT,
    actual_check_out    TEXT,
    check_in_by         INTEGER REFERENCES staff(staff_id),
    check_out_by        INTEGER REFERENCES staff(staff_id),
    check_in_notes      TEXT,
    check_out_notes     TEXT,
    room_condition      TEXT    NOT NULL DEFAULT 'good',
    damage_description  TEXT,
    damage_charge       REAL    NOT NULL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS service (
    service_id      SERIAL PRIMARY KEY,
    service_name    TEXT    NOT NULL,
    category        TEXT    NOT NULL,
    unit_price      REAL    NOT NULL,
    unit            TEXT,
    description     TEXT,
    is_available    INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS charge (
    charge_id       SERIAL PRIMARY KEY,
    reservation_id  INTEGER NOT NULL REFERENCES reservation(reservation_id),
    service_id      INTEGER NOT NULL REFERENCES service(service_id),
    quantity        REAL    NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    charge_date     TEXT    NOT NULL,
    staff_id        INTEGER REFERENCES staff(staff_id),
    notes           TEXT,
    is_voided       INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoice (
    invoice_id          SERIAL PRIMARY KEY,
    invoice_code        TEXT    NOT NULL UNIQUE,
    reservation_id      INTEGER NOT NULL REFERENCES reservation(reservation_id),
    issue_date          TEXT    NOT NULL,
    due_date            TEXT,
    room_charges        REAL    NOT NULL DEFAULT 0.0,
    service_charges     REAL    NOT NULL DEFAULT 0.0,
    damage_charges      REAL    NOT NULL DEFAULT 0.0,
    subtotal            REAL    NOT NULL DEFAULT 0.0,
    discount_amount     REAL    NOT NULL DEFAULT 0.0,
    tax_rate            REAL    NOT NULL DEFAULT 10.0,
    tax_amount          REAL    NOT NULL DEFAULT 0.0,
    total_amount        REAL    NOT NULL DEFAULT 0.0,
    paid_amount         REAL    NOT NULL DEFAULT 0.0,
    balance_due         REAL    NOT NULL DEFAULT 0.0,
    currency            TEXT    NOT NULL DEFAULT 'VND',
    status              TEXT    NOT NULL DEFAULT 'draft',
    issued_by           INTEGER REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS payment (
    payment_id      SERIAL PRIMARY KEY,
    invoice_id      INTEGER NOT NULL REFERENCES invoice(invoice_id),
    amount          REAL    NOT NULL,
    payment_method  TEXT    NOT NULL,
    payment_date    TEXT    NOT NULL,
    transaction_ref TEXT,
    card_last4      TEXT,
    card_type       TEXT,
    is_deposit      INTEGER NOT NULL DEFAULT 0,
    status          TEXT    NOT NULL DEFAULT 'completed',
    processed_by    INTEGER REFERENCES staff(staff_id),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS housekeeping_task (
    task_id         SERIAL PRIMARY KEY,
    room_id         INTEGER NOT NULL REFERENCES room(room_id),
    task_type       TEXT    NOT NULL,
    assigned_to     INTEGER REFERENCES staff(staff_id),
    task_date       TEXT    NOT NULL,
    scheduled_time  TEXT,
    started_at      TEXT,
    completed_at    TEXT,
    status          TEXT    NOT NULL DEFAULT 'pending',
    notes           TEXT,
    checked_by      INTEGER REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS minibar_item (
    item_id         SERIAL PRIMARY KEY,
    item_name       TEXT    NOT NULL,
    unit_price      REAL    NOT NULL,
    category        TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS minibar_consumption (
    id              SERIAL PRIMARY KEY,
    reservation_id  INTEGER NOT NULL REFERENCES reservation(reservation_id),
    item_id         INTEGER NOT NULL REFERENCES minibar_item(item_id),
    quantity        REAL    NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    recorded_at     TEXT    NOT NULL,
    recorded_by     INTEGER REFERENCES staff(staff_id)
);

CREATE TABLE IF NOT EXISTS maintenance_request (
    request_id      SERIAL PRIMARY KEY,
    room_id         INTEGER NOT NULL REFERENCES room(room_id),
    issue_type      TEXT    NOT NULL,
    description     TEXT,
    priority        TEXT    NOT NULL DEFAULT 'medium',
    status          TEXT    NOT NULL DEFAULT 'open',
    reported_by     INTEGER REFERENCES staff(staff_id),
    assigned_to     INTEGER REFERENCES staff(staff_id),
    reported_at     TEXT    NOT NULL,
    started_at      TEXT,
    resolved_at     TEXT,
    resolution_note TEXT
);

CREATE TABLE IF NOT EXISTS review (
    review_id           SERIAL PRIMARY KEY,
    reservation_id      INTEGER NOT NULL REFERENCES reservation(reservation_id),
    guest_id            INTEGER NOT NULL REFERENCES guest(guest_id),
    overall_rating      INTEGER NOT NULL,
    cleanliness         INTEGER,
    service             INTEGER,
    location            INTEGER,
    value_for_money     INTEGER,
    comment             TEXT,
    staff_reply         TEXT,
    replied_by          INTEGER REFERENCES staff(staff_id),
    replied_at          TEXT,
    source              TEXT    NOT NULL DEFAULT 'internal',
    is_published        INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS audit_log (
    log_id          SERIAL PRIMARY KEY,
    table_name      TEXT    NOT NULL,
    record_id       INTEGER NOT NULL,
    action          TEXT    NOT NULL,
    old_data        TEXT,
    new_data        TEXT,
    performed_by    INTEGER REFERENCES staff(staff_id),
    performed_at    TEXT    NOT NULL,
    ip_address      TEXT,
    notes           TEXT
);
