-- Таблицы для сырых данных из Google Sheets

-- Таблица "Директ" (рекламный бюджет + ФОТ директ)
CREATE TABLE IF NOT EXISTS sheets_raw_direct (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,  -- Торговое предприятие
    ad_budget NUMERIC(15, 2),  -- Рекламный бюджет
    fot_direct NUMERIC(15, 2),  -- ФОТ директ
    raw_data JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department)
);

CREATE INDEX idx_sheets_raw_direct_date ON sheets_raw_direct(report_date);
CREATE INDEX idx_sheets_raw_direct_department ON sheets_raw_direct(department);

-- Таблица ФОТ (курьеры, повара, уборщицы)
-- Структура может отличаться, поэтому используем гибкую схему
CREATE TABLE IF NOT EXISTS sheets_raw_fot (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    department VARCHAR(255) NOT NULL,
    fot_couriers NUMERIC(15, 2),  -- ФОТ курьеры
    fot_cooks NUMERIC(15, 2),  -- ФОТ повара
    fot_cleaners NUMERIC(15, 2),  -- ФОТ уборщицы
    raw_data JSONB,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_date, department)
);

CREATE INDEX idx_sheets_raw_fot_date ON sheets_raw_fot(report_date);
CREATE INDEX idx_sheets_raw_fot_department ON sheets_raw_fot(department);
