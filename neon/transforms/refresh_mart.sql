-- SQL трансформации для расчета всех 15 метрик в витрине данных

-- Очистка витрины перед обновлением (опционально, можно использовать UPSERT)
-- TRUNCATE TABLE mart_daily_metrics;
-- TRUNCATE TABLE mart_hourly_load;
-- TRUNCATE TABLE mart_discount_types;

-- 1. Обновление таблицы mart_daily_metrics (метрики по дням)

INSERT INTO mart_daily_metrics (
    report_date,
    department,
    revenue,
    discount_percent,
    cost_percent,
    ad_budget,
    ad_budget_percent,
    fot_direct,
    fot_direct_percent,
    fot_couriers,
    fot_couriers_percent,
    fot_cooks,
    fot_cooks_percent,
    fot_cleaners,
    fot_cleaners_percent,
    packaging_cost,
    arora_cost,
    taxes_cost,
    acquiring_cost,
    margin
)
SELECT 
    m.report_date,
    m.department,
    -- Метрики из iiko (п.1, 2, 4)
    m.dish_sum_int AS revenue,  -- 1) Выручка по дням
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (m.discount_sum / m.dish_sum_int * 100)
        ELSE 0 
    END AS discount_percent,  -- 2) % скидки по дням
    m.product_cost_base_percent AS cost_percent,  -- 4) % себестоимости
    
    -- Метрики из Google Sheets (п.3, 5, 11, 12)
    COALESCE(d.ad_budget, 0) AS ad_budget,  -- 3) Рекламный бюджет
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (COALESCE(d.ad_budget, 0) / m.dish_sum_int * 100)
        ELSE 0 
    END AS ad_budget_percent,  -- 3) % рекламный бюджет
    COALESCE(d.fot_direct, 0) AS fot_direct,  -- 3) ФОТ директ
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (COALESCE(d.fot_direct, 0) / m.dish_sum_int * 100)
        ELSE 0 
    END AS fot_direct_percent,  -- 3) % ФОТ директ
    
    COALESCE(f.fot_couriers, 0) AS fot_couriers,  -- 5) ФОТ курьеры
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (COALESCE(f.fot_couriers, 0) / m.dish_sum_int * 100)
        ELSE 0 
    END AS fot_couriers_percent,  -- 5) % ФОТ курьеры
    
    COALESCE(f.fot_cooks, 0) AS fot_cooks,  -- 11) ФОТ повара
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (COALESCE(f.fot_cooks, 0) / m.dish_sum_int * 100)
        ELSE 0 
    END AS fot_cooks_percent,  -- 11) % ФОТ повара
    
    COALESCE(f.fot_cleaners, 0) AS fot_cleaners,  -- 12) ФОТ уборщицы
    CASE 
        WHEN m.dish_sum_int > 0 
        THEN (COALESCE(f.fot_cleaners, 0) / m.dish_sum_int * 100)
        ELSE 0 
    END AS fot_cleaners_percent,  -- 12) % ФОТ уборщицы
    
    -- Расчетные метрики (п.6-9) - проценты от выручки
    m.dish_sum_int * 0.028 AS packaging_cost,  -- 6) Упаковка: 2.8% от выручки
    m.dish_sum_int * 0.014 AS arora_cost,  -- 7) Арору: 1.4% от выручки
    m.dish_sum_int * 0.011 AS taxes_cost,  -- 8) Налоги: 1.1% от выручки
    m.dish_sum_int * 0.008 AS acquiring_cost,  -- 9) Эквайринг: 0.8% от выручки
    
    -- Итоговая маржа (п.10): выручка - себестоимость - все расходы
    m.dish_sum_int 
    - (m.dish_sum_int * m.product_cost_base_percent / 100)  -- себестоимость
    - COALESCE(d.ad_budget, 0)  -- рекламный бюджет
    - COALESCE(d.fot_direct, 0)  -- ФОТ директ
    - COALESCE(f.fot_couriers, 0)  -- ФОТ курьеры
    - COALESCE(f.fot_cooks, 0)  -- ФОТ повара
    - COALESCE(f.fot_cleaners, 0)  -- ФОТ уборщицы
    - (m.dish_sum_int * 0.028)  -- упаковка
    - (m.dish_sum_int * 0.014)  -- арору
    - (m.dish_sum_int * 0.011)  -- налоги
    - (m.dish_sum_int * 0.008)  -- эквайринг
    AS margin
    
FROM iiko_raw_margin m
LEFT JOIN sheets_raw_direct d 
    ON m.report_date = d.report_date 
    AND m.department = d.department
LEFT JOIN sheets_raw_fot f 
    ON m.report_date = f.report_date 
    AND m.department = f.department
ON CONFLICT (report_date, department) 
DO UPDATE SET
    revenue = EXCLUDED.revenue,
    discount_percent = EXCLUDED.discount_percent,
    cost_percent = EXCLUDED.cost_percent,
    ad_budget = EXCLUDED.ad_budget,
    ad_budget_percent = EXCLUDED.ad_budget_percent,
    fot_direct = EXCLUDED.fot_direct,
    fot_direct_percent = EXCLUDED.fot_direct_percent,
    fot_couriers = EXCLUDED.fot_couriers,
    fot_couriers_percent = EXCLUDED.fot_couriers_percent,
    fot_cooks = EXCLUDED.fot_cooks,
    fot_cooks_percent = EXCLUDED.fot_cooks_percent,
    fot_cleaners = EXCLUDED.fot_cleaners,
    fot_cleaners_percent = EXCLUDED.fot_cleaners_percent,
    packaging_cost = EXCLUDED.packaging_cost,
    arora_cost = EXCLUDED.arora_cost,
    taxes_cost = EXCLUDED.taxes_cost,
    acquiring_cost = EXCLUDED.acquiring_cost,
    margin = EXCLUDED.margin,
    updated_at = CURRENT_TIMESTAMP;

-- 2. Обновление таблицы mart_hourly_load (нагрузка по часам, п.13, 14)

INSERT INTO mart_hourly_load (
    report_date,
    department,
    hour_open,
    orders_count,
    revenue
)
SELECT 
    COALESCE(o.report_date, r.report_date) AS report_date,
    COALESCE(o.department, r.department) AS department,
    COALESCE(o.hour_open, r.hour_open) AS hour_open,
    COALESCE(o.orders_count, 0) AS orders_count,  -- 13) Нагрузка по дням и по часам по кол-ву заказов
    COALESCE(r.dish_discount_sum_int, 0) AS revenue  -- 14) Нагрузка по дням и по часам по выручке
FROM iiko_raw_load_orders o
FULL OUTER JOIN iiko_raw_load_revenue r
    ON o.report_date = r.report_date
    AND o.department = r.department
    AND o.hour_open = r.hour_open
ON CONFLICT (report_date, department, hour_open)
DO UPDATE SET
    orders_count = EXCLUDED.orders_count,
    revenue = EXCLUDED.revenue,
    updated_at = CURRENT_TIMESTAMP;

-- 3. Обновление таблицы mart_discount_types (типы скидок, п.15)

INSERT INTO mart_discount_types (
    report_date,
    department,
    discount_type,
    orders_count,
    revenue_with_discount,
    discount_sum,
    average_check
)
SELECT 
    report_date,
    department,
    discount_type,
    orders_count,  -- Количество заказов со скидкой
    dish_discount_sum_int AS revenue_with_discount,  -- Выручка с заказов со скидкой
    discount_sum,  -- Сумма общей по скидке
    average_order_sum AS average_check  -- Средний чек по заказам со скидкой
FROM iiko_raw_discount_types
ON CONFLICT (report_date, department, discount_type)
DO UPDATE SET
    orders_count = EXCLUDED.orders_count,
    revenue_with_discount = EXCLUDED.revenue_with_discount,
    discount_sum = EXCLUDED.discount_sum,
    average_check = EXCLUDED.average_check,
    updated_at = CURRENT_TIMESTAMP;
