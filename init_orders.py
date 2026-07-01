from datetime import date
import duckdb

con = duckdb.connect()
con.execute("INSTALL fakeit FROM community; LOAD fakeit;")

# ---------------------------------------------------------------------------
# Глобальные переменные — объём данных
# ---------------------------------------------------------------------------
ORDERS_VALUE = 15_000_000
CUSTOMER_POOL = 1_200_000
EMPLOYEE_POOL = 1_000
CITY_POOL = 150
OVERSAMPLE_FACTOR = 1.5  # запас для взвешенной выборки дат

# ---------------------------------------------------------------------------
# Глобальные переменные — диапазон дат
# ---------------------------------------------------------------------------
DATE_FROM = date(2020, 1, 1)
DATE_TO = date(2026, 1, 1)

# Количество дней вычисляется автоматически — не нужно считать вручную
DATE_RANGE_DAYS = (DATE_TO - DATE_FROM).days

# Веса сезонности (1.0 = базовый уровень, >1.0 = пик, <1.0 = спад)
WEIGHT_NEW_YEAR = 3.0    # 20 дек — 10 янв: новогодний пик
WEIGHT_MARCH_8 = 1.6     # 1–8 марта: 8 марта
WEIGHT_FEB_14 = 1.4      # 10–14 февраля: 14 февраля
WEIGHT_FEB_23 = 1.3      # 20–23 февраля: 23 февраля
WEIGHT_SCHOOL = 1.3      # 15–31 августа: подготовка к школе
WEIGHT_SUMMER = 0.75     # июнь–июль: летний спад
WEIGHT_BASE = 1.0        # всё остальное

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

-- Генерируем избыточный пул дат для взвешенной выборки
candidate_dates AS (
    SELECT order_date
    FROM (
        SELECT
            TIMESTAMP '{DATE_FROM}'
                + (random() * {DATE_RANGE_DAYS})::INT * INTERVAL 1 DAY
                + (random() * 86399)::INT * INTERVAL 1 SECOND AS order_date
        FROM generate_series(1, ({ORDERS_VALUE} * {OVERSAMPLE_FACTOR})::BIGINT)
    )
    WHERE order_date < TIMESTAMP '{DATE_TO}'
),

-- Назначаем вес каждой дате по сезонным правилам
weighted_dates AS (
    SELECT
        order_date,
        CASE
            WHEN (MONTH(order_date) = 12 AND DAY(order_date) >= 20)
              OR (MONTH(order_date) = 1 AND DAY(order_date) <= 10) THEN {WEIGHT_NEW_YEAR}
            WHEN MONTH(order_date) = 3 AND DAY(order_date) BETWEEN 1 AND 8 THEN {WEIGHT_MARCH_8}
            WHEN MONTH(order_date) = 2 AND DAY(order_date) BETWEEN 10 AND 14 THEN {WEIGHT_FEB_14}
            WHEN MONTH(order_date) = 2 AND DAY(order_date) BETWEEN 20 AND 23 THEN {WEIGHT_FEB_23}
            WHEN MONTH(order_date) = 8 AND DAY(order_date) >= 15 THEN {WEIGHT_SCHOOL}
            WHEN MONTH(order_date) IN (6, 7) THEN {WEIGHT_SUMMER}
            ELSE {WEIGHT_BASE}
        END AS season_weight
    FROM candidate_dates
),

-- A-Res: взвешенная выборка без повторов — даты с высоким весом
-- чаще попадают в финальную выборку
sampled_dates AS (
    SELECT order_date
    FROM weighted_dates
    ORDER BY POWER(random(), 1.0 / season_weight) DESC
    LIMIT {ORDERS_VALUE}
),

base AS (
    SELECT
        fakeit_uuid_v4() AS order_id,
        cp.uuids[(random() * {CUSTOMER_POOL})::INT + 1] AS customer_id,
        ep.uuids[(random() * {EMPLOYEE_POOL})::INT + 1] AS employee_id,
        ctp.uuids[(random() * {CITY_POOL})::INT + 1] AS ship_city_id,
        (random() * 6)::INT + 1 AS ship_id,
        sd.order_date AS order_date,
        random() AS ship_roll,
        random() AS receipt_day_roll,
        random() AS receipt_time_roll
    FROM sampled_dates sd
    CROSS JOIN customer_pool cp
    CROSS JOIN employee_pool ep
    CROSS JOIN city_pool ctp
),

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

with_base_time AS (
    SELECT
        *,
        CASE
            WHEN shipped_date::TIME BETWEEN '08:00:00' AND '22:00:00' THEN shipped_date
            ELSE (shipped_date::DATE + INTERVAL 1 DAY) + INTERVAL 8 HOUR
        END AS base_time
    FROM with_shipped
),

with_receipt AS (
    SELECT
        *,
        base_time::DATE + (receipt_day_roll * 7)::INT * INTERVAL 1 DAY AS receipt_day,
        INTERVAL 8 HOUR + (receipt_time_roll * 14 * 3600)::INT * INTERVAL 1 SECOND AS receipt_time_offset
    FROM with_base_time
),

with_receipt_date AS (
    SELECT *, receipt_day + receipt_time_offset AS receipt_date_raw FROM with_receipt
)

SELECT
    order_id,
    customer_id,
    employee_id,
    ship_city_id,
    ship_id,
    order_date,
    shipped_date,
    CASE
        WHEN receipt_date_raw <= shipped_date THEN shipped_date + INTERVAL 1 SECOND
        ELSE receipt_date_raw
    END AS receipt_date,
    ROUND(POWER(10, 1 + random() * (LOG10(500000) - 1)), 2) AS amount
FROM with_receipt_date
""")

con.query("COPY orders TO 'orders.parquet'")

con.close()