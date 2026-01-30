-- Начальная схема Neon для маркетинговой аналитики.
-- Таблица сырых выгрузок iiko и витрины для DataLens.

-- Сырые данные: ответ API iiko (JSONB)
CREATE TABLE IF NOT EXISTS iiko_raw_export (
    id SERIAL PRIMARY KEY,
    exported_at TIMESTAMPTZ DEFAULT NOW(),
    payload JSONB NOT NULL
);

-- Витрина: продажи по дням и точкам для DataLens
CREATE TABLE IF NOT EXISTS mart_sales_by_day (
    id SERIAL PRIMARY KEY,
    report_date DATE NOT NULL,
    organization_id TEXT,
    organization_name TEXT,
    revenue NUMERIC(14, 2) DEFAULT 0,
    orders_count INTEGER DEFAULT 0,
    avg_check NUMERIC(14, 2),
    refreshed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (report_date, organization_id)
);

CREATE INDEX IF NOT EXISTS idx_mart_sales_by_day_date ON mart_sales_by_day (report_date);
CREATE INDEX IF NOT EXISTS idx_mart_sales_by_day_org ON mart_sales_by_day (organization_id);
CREATE INDEX IF NOT EXISTS idx_iiko_raw_export_exported ON iiko_raw_export (exported_at);
