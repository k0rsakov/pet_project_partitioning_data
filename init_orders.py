import duckdb

con = duckdb.connect()
con.execute("INSTALL fakeit FROM community; LOAD fakeit;")

# ---------------------------------------------------------------------------
# Глобальные переменные
# ---------------------------------------------------------------------------
ORDERS_VALUE = 15_000_000
CUSTOMER_POOL = 1_200_000
EMPLOYEE_POOL = 1_000
CITY_POOL = 150

# ---------------------------------------------------------------------------
# Справочник способов доставки
# ---------------------------------------------------------------------------
con.execute(
    """
    CREATE OR REPLACE TABLE ship_types (
        ship_id INTEGER PRIMARY KEY,
        ship_name VARCHAR,
        min_delay_days INTEGER,
        max_delay_days INTEGER
    );
    
    INSERT INTO ship_types VALUES
        (1, 'Самовывоз', 0, 30),
        (2, 'Курьер пеший', 0, 30),
        (3, 'Курьер СИМ', 0, 30),
        (4, 'Курьер авто', 0, 30),
        (5, 'Доставка межгород авто', 1, 15),
        (6, 'Доставка межгород авиа', 2, 10),
    (7, 'Доставка межгород вода', 30, 120);
    """
)

# ---------------------------------------------------------------------------
# Основная таблица orders
# ---------------------------------------------------------------------------
con.execute(f"""
CREATE OR REPLACE TABLE orders AS
WITH customer_pool AS (
    SELECT array_agg(fakeit_uuid_v4()) AS uuids FROM generate_series(1, {CUSTOMER_POOL})
),
employee_pool AS (
    SELECT array_agg(fakeit_uuid_v4()) AS uuids FROM generate_series(1, {EMPLOYEE_POOL})
),
city_pool AS (
    SELECT array_agg(fakeit_uuid_v4()) AS uuids FROM generate_series(1, {CITY_POOL})
),

-- Базовая генерация заказа: даты ещё не считаем, только сырьё
base AS (
    SELECT
        fakeit_uuid_v4() AS order_id,
        cp.uuids[(random() * {CUSTOMER_POOL})::INT + 1] AS customer_id,
        ep.uuids[(random() * {EMPLOYEE_POOL})::INT + 1] AS employee_id,
        ctp.uuids[(random() * {CITY_POOL})::INT + 1] AS ship_city_id,
        (random() * 6)::INT + 1 AS ship_id,
        TIMESTAMP '2022-01-01' + (random() * 1095)::INT * INTERVAL 1 DAY
            + (random() * 86399)::INT * INTERVAL 1 SECOND AS order_date,
        random() AS ship_roll,
        random() AS receipt_day_roll,
        random() AS receipt_time_roll
    FROM generate_series(1, {ORDERS_VALUE})
    CROSS JOIN customer_pool cp
    CROSS JOIN employee_pool ep
    CROSS JOIN city_pool ctp
),

-- Считаем shipped_date: с вероятностью 30% совпадает с order_date,
-- с вероятностью 70% сдвигается на диапазон, зависящий от ship_id
with_shipped AS (
    SELECT
        base.*,
        st.min_delay_days,
        st.max_delay_days,
        CASE
            WHEN ship_roll < 0.3 THEN order_date
            ELSE order_date
                + (st.min_delay_days + random() * (st.max_delay_days - st.min_delay_days))::INT * INTERVAL 1 DAY
                + (random() * 86399)::INT * INTERVAL 1 SECOND
        END AS shipped_date
    FROM base
    JOIN ship_types st USING (ship_id)
),

-- Приводим shipped_date к рабочему окну: если время вне 08:00-22:00,
-- base_time переносится на ближайшие 08:00 следующего дня
with_base_time AS (
    SELECT
        *,
        CASE
            WHEN shipped_date::TIME BETWEEN '08:00:00' AND '22:00:00' THEN shipped_date
            ELSE (shipped_date::DATE + INTERVAL 1 DAY) + INTERVAL 8 HOUR
        END AS base_time
    FROM with_shipped
),

-- Считаем receipt_date: день получения 0-7 от base_time,
-- время получения случайное в пределах 08:00-22:00 того дня
with_receipt AS (
    SELECT
        *,
        base_time::DATE + (receipt_day_roll * 7)::INT * INTERVAL 1 DAY AS receipt_day,
        INTERVAL 8 HOUR + (receipt_time_roll * 14 * 3600)::INT * INTERVAL 1 SECOND AS receipt_time_offset
    FROM with_base_time
),

with_receipt_date AS (
    SELECT
        *,
        receipt_day + receipt_time_offset AS receipt_date_raw
    FROM with_receipt
)

SELECT
    order_id,
    customer_id,
    employee_id,
    ship_city_id,
    ship_id,
    order_date,
    shipped_date,
    -- Гарантируем receipt_date > shipped_date минимум на 1 секунду,
    -- если случайно выбранный момент оказался раньше или равен base_time
    CASE
        WHEN receipt_date_raw <= shipped_date THEN shipped_date + INTERVAL 1 SECOND
        ELSE receipt_date_raw
    END AS receipt_date,
    ROUND(POWER(10, 1 + random() * (LOG10(500000) - 1)), 2) AS amount
FROM with_receipt_date
""")

con.query(
    """
    COPY orders TO 'orders.parquet'
    """
)

con.close()