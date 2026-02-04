-- Витрина данных для DataLens со всеми 15 метриками

CREATE TABLE IF NOT EXISTS mart_daily_metrics (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,  -- Торговое предприятие (Домодедово/Авиагородок)
    
    -- Метрики из iiko (п.1, 2, 4)
    revenue NUMERIC(15, 2),  -- 1) Выручка по дням (доставка + самовывоз)
    discount_percent NUMERIC(5, 2),  -- 2) % скидки по дням
    cost_percent NUMERIC(5, 2),  -- 4) % себестоимости
    
    -- Метрики из Google Sheets (п.3, 5, 11, 12)
    ad_budget NUMERIC(15, 2),  -- 3) Рекламный бюджет
    ad_budget_percent NUMERIC(5, 2),  -- 3) % рекламный бюджет (от выручки)
    fot_direct NUMERIC(15, 2),  -- 3) ФОТ директ
    fot_direct_percent NUMERIC(5, 2),  -- 3) % ФОТ директ (от выручки)
    fot_couriers NUMERIC(15, 2),  -- 5) ФОТ курьеры
    fot_couriers_percent NUMERIC(5, 2),  -- 5) % ФОТ курьеры (от выручки)
    fot_cooks NUMERIC(15, 2),  -- 11) ФОТ повара
    fot_cooks_percent NUMERIC(5, 2),  -- 11) % ФОТ повара (от выручки)
    fot_cleaners NUMERIC(15, 2),  -- 12) ФОТ уборщицы
    fot_cleaners_percent NUMERIC(5, 2),  -- 12) % ФОТ уборщицы (от выручки)
    
    -- Расчетные метрики (п.6-9)
    packaging_cost NUMERIC(15, 2),  -- 6) Потрачено руб на Упаковку (2.8% от выручки)
    arora_cost NUMERIC(15, 2),  -- 7) Потрачено руб на Арору (1.4% от выручки)
    taxes_cost NUMERIC(15, 2),  -- 8) Потрачено руб на Налоги (1.1% от выручки)
    acquiring_cost NUMERIC(15, 2),  -- 9) Потрачено руб на Эквайринг (0.8% от выручки)
    
    -- Итоговая метрика (п.10)
    margin NUMERIC(15, 2),  -- 10) Итого маржа по дням
    
    -- Метаданные
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department)
);

CREATE INDEX idx_mart_daily_metrics_date ON mart_daily_metrics(report_date);
CREATE INDEX idx_mart_daily_metrics_department ON mart_daily_metrics(department);

-- Таблица нагрузки по часам (п.13, 14)
CREATE TABLE IF NOT EXISTS mart_hourly_load (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    hour_open INTEGER NOT NULL,  -- Час (0-23)
    orders_count INTEGER,  -- 13) Нагрузка по дням и по часам по кол-ву заказов
    revenue NUMERIC(15, 2),  -- 14) Нагрузка по дням и по часам по выручке
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department, hour_open)
);

CREATE INDEX idx_mart_hourly_load_date ON mart_hourly_load(report_date);
CREATE INDEX idx_mart_hourly_load_department ON mart_hourly_load(department);
CREATE INDEX idx_mart_hourly_load_hour ON mart_hourly_load(hour_open);

-- Таблица типов скидок (п.15)
CREATE TABLE IF NOT EXISTS mart_discount_types (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    discount_type VARCHAR(255) NOT NULL,  -- Тип скидки
    orders_count INTEGER,  -- Количество заказов со скидкой
    revenue_with_discount NUMERIC(15, 2),  -- Выручка с заказов со скидкой
    discount_sum NUMERIC(15, 2),  -- Сумма общей по скидке
    average_check NUMERIC(15, 2),  -- Средний чек по заказам со скидкой
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department, discount_type)
);

CREATE INDEX idx_mart_discount_types_date ON mart_discount_types(report_date);
CREATE INDEX idx_mart_discount_types_department ON mart_discount_types(department);
CREATE INDEX idx_mart_discount_types_type ON mart_discount_types(discount_type);
