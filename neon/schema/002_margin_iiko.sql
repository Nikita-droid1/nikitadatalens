-- Маржа по дням и департаментам (iiko OLAP).
-- Заполняется etl_iiko_margin_daily. См. docs/iiko-etl-colleague-reference.md.

CREATE TABLE IF NOT EXISTS margin_iiko (
    department TEXT NOT NULL,
    oper_day DATE NOT NULL,
    revenue NUMERIC(14, 2) DEFAULT 0,
    discount NUMERIC(14, 2) DEFAULT 0,
    product_cost NUMERIC(14, 2) DEFAULT 0,
    revenue_courier NUMERIC(14, 2) DEFAULT 0,
    discount_courier NUMERIC(14, 2) DEFAULT 0,
    product_cost_courier NUMERIC(14, 2) DEFAULT 0,
    revenue_pickup NUMERIC(14, 2) DEFAULT 0,
    discount_pickup NUMERIC(14, 2) DEFAULT 0,
    product_cost_pickup NUMERIC(14, 2) DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (department, oper_day)
);

CREATE INDEX IF NOT EXISTS idx_margin_iiko_oper_day ON margin_iiko (oper_day);
CREATE INDEX IF NOT EXISTS idx_margin_iiko_department ON margin_iiko (department);
