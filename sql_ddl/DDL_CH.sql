-- Справочник способов доставки
CREATE TABLE ship_types (
    ship_id   UInt8,
    ship_name String
) ENGINE = MergeTree()
ORDER BY ship_id;

INSERT INTO ship_types VALUES
    (1, 'Самовывоз'),
    (2, 'Курьер пеший'),
    (3, 'Курьер СИМ'),
    (4, 'Курьер авто'),
    (5, 'Доставка межгород авто'),
    (6, 'Доставка межгород авиа'),
    (7, 'Доставка межгород вода');

-- Основная таблица orders
CREATE TABLE orders (
    order_id      UUID,
    customer_id   UUID,
    employee_id   UUID,
    ship_city_id  UUID,
    ship_id       UInt8,
    order_date    DateTime,
    shipped_date  Nullable(DateTime),
    receipt_date  Nullable(DateTime),
    amount        Decimal(12, 2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_date)
ORDER BY (order_date, order_id);