-- Таблицы для сырых данных из iiko Server API

-- Отчет "Маржа" (выручка, % скидки, % себестоимости)
CREATE TABLE IF NOT EXISTS iiko_raw_margin (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,  -- Торговое предприятие (Домодедово/Авиагородок)
    dish_sum_int NUMERIC(15, 2),  -- Сумма без скидки (выручка)
    discount_sum NUMERIC(15, 2),  -- Сумма скидки
    product_cost_base_percent NUMERIC(5, 2),  -- Себестоимость (%)
    raw_data JSONB,  -- Полные сырые данные отчета
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department)
);

CREATE INDEX idx_iiko_raw_margin_date ON iiko_raw_margin(report_date);
CREATE INDEX idx_iiko_raw_margin_department ON iiko_raw_margin(department);

-- Отчет "Нагрузка по часам (заказы)"
CREATE TABLE IF NOT EXISTS iiko_raw_load_orders (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    hour_open INTEGER NOT NULL,  -- Час открытия (0-23)
    orders_count INTEGER,  -- Количество заказов
    raw_data JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department, hour_open)
);

CREATE INDEX idx_iiko_raw_load_orders_date ON iiko_raw_load_orders(report_date);
CREATE INDEX idx_iiko_raw_load_orders_department ON iiko_raw_load_orders(department);
CREATE INDEX idx_iiko_raw_load_orders_hour ON iiko_raw_load_orders(hour_open);

-- Отчет "Нагрузка по часам (выручка)"
CREATE TABLE IF NOT EXISTS iiko_raw_load_revenue (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    hour_open INTEGER NOT NULL,
    dish_discount_sum_int NUMERIC(15, 2),  -- Сумма со скидкой (выручка)
    raw_data JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department, hour_open)
);

CREATE INDEX idx_iiko_raw_load_revenue_date ON iiko_raw_load_revenue(report_date);
CREATE INDEX idx_iiko_raw_load_revenue_department ON iiko_raw_load_revenue(department);
CREATE INDEX idx_iiko_raw_load_revenue_hour ON iiko_raw_load_revenue(hour_open);

-- Отчет "Типы скидок"
CREATE TABLE IF NOT EXISTS iiko_raw_discount_types (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    discount_type VARCHAR(255) NOT NULL,  -- Тип скидки
    orders_count INTEGER,  -- Количество заказов со скидкой
    dish_discount_sum_int NUMERIC(15, 2),  -- Сумма со скидкой
    discount_sum NUMERIC(15, 2),  -- Сумма скидки
    average_order_sum NUMERIC(15, 2),  -- Средний чек
    raw_data JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department, discount_type)
);

CREATE INDEX idx_iiko_raw_discount_types_date ON iiko_raw_discount_types(report_date);
CREATE INDEX idx_iiko_raw_discount_types_department ON iiko_raw_discount_types(department);
CREATE INDEX idx_iiko_raw_discount_types_type ON iiko_raw_discount_types(discount_type);
