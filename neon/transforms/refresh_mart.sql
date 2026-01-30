-- Постобработка: заполнение витрины mart_sales_by_day из iiko_raw_export.
-- Структура payload зависит от ответа iiko Server (Resto) API. Текущий разбор — под формат iikoCloud (payload.ordersByOrganizations[] { organizationId, orders[] { order: { sum, whenCreated } } }); под Resto API нужно адаптировать пути JSONB после получения реального ответа (см. docs/iiko-server-api.md).
-- Запуск: выполнить скрипт после выгрузки из iiko (вручную или из GitHub Action).

WITH orders_flat AS (
  SELECT
    r.id AS export_id,
    org->>'organizationId' AS organization_id,
    ord->'order'->>'sum' AS order_sum,
    ord->'order'->>'whenCreated' AS when_created
  FROM iiko_raw_export r,
       LATERAL jsonb_array_elements(COALESCE(r.payload->'ordersByOrganizations', '[]'::jsonb)) AS org,
       LATERAL jsonb_array_elements(COALESCE(org->'orders', '[]'::jsonb)) AS ord
  WHERE r.exported_at >= NOW() - INTERVAL '30 days'
    AND org->>'organizationId' IS NOT NULL
    AND org->>'organizationId' <> ''
    AND ord->'order' IS NOT NULL
    AND (ord->'order'->>'whenCreated') IS NOT NULL
    AND (ord->'order'->>'sum') IS NOT NULL
),
agg AS (
  SELECT
    (when_created::timestamp)::date AS report_date,
    organization_id,
    SUM((order_sum)::numeric) AS revenue,
    COUNT(*)::integer AS orders_count,
    AVG((order_sum)::numeric) AS avg_check
  FROM orders_flat
  GROUP BY (when_created::timestamp)::date, organization_id
)
INSERT INTO mart_sales_by_day (report_date, organization_id, organization_name, revenue, orders_count, avg_check, refreshed_at)
SELECT
  report_date,
  organization_id,
  NULL AS organization_name,
  revenue,
  orders_count,
  avg_check,
  NOW() AS refreshed_at
FROM agg
ON CONFLICT (report_date, organization_id) DO UPDATE SET
  revenue = EXCLUDED.revenue,
  orders_count = EXCLUDED.orders_count,
  avg_check = EXCLUDED.avg_check,
  refreshed_at = EXCLUDED.refreshed_at;
