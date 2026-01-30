-- Нагрузка по часам (iiko OLAP «Нагрузка по часам»).
-- Заполняется etl_iiko_load_hourly. См. docs/iiko-etl-colleague-reference.md.

CREATE TABLE IF NOT EXISTS load_hourly_iiko (
    department TEXT NOT NULL,
    oper_day DATE NOT NULL,
    hour INTEGER NOT NULL,
    orders_count INTEGER DEFAULT 0,
    revenue NUMERIC(14, 2) DEFAULT 0,
    discount NUMERIC(14, 2) DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (department, oper_day, hour)
);

CREATE INDEX IF NOT EXISTS idx_load_hourly_iiko_oper_day ON load_hourly_iiko (oper_day);
CREATE INDEX IF NOT EXISTS idx_load_hourly_iiko_department ON load_hourly_iiko (department);
CREATE INDEX IF NOT EXISTS idx_load_hourly_iiko_hour ON load_hourly_iiko (hour);
