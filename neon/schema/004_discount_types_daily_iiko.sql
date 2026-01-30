-- Типы скидок по дням (iiko OLAP «Типы скидок»).
-- Заполняется etl_iiko_discount_types_daily. См. docs/iiko-etl-colleague-reference.md.

CREATE TABLE IF NOT EXISTS discount_types_daily_iiko (
    department TEXT NOT NULL,
    oper_day DATE NOT NULL,
    discount_type TEXT NOT NULL,
    orders_count INTEGER DEFAULT 0,
    revenue NUMERIC(14, 2) DEFAULT 0,
    discount_sum NUMERIC(14, 2) DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (department, oper_day, discount_type)
);

CREATE INDEX IF NOT EXISTS idx_discount_types_daily_oper_day ON discount_types_daily_iiko (oper_day);
CREATE INDEX IF NOT EXISTS idx_discount_types_daily_department ON discount_types_daily_iiko (department);
CREATE INDEX IF NOT EXISTS idx_discount_types_daily_type ON discount_types_daily_iiko (discount_type);
