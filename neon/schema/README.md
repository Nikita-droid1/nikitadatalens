# Схема БД Neon

**Назначение:** описание таблиц и структуры данных в Neon.

## Таблицы

- **iiko_raw_export** — сырые выгрузки: ответ API iiko в JSONB (id, exported_at, payload).
- **mart_sales_by_day** — витрина для DataLens: report_date, organization_id, organization_name, revenue, orders_count, avg_check, refreshed_at.

## Файлы

- **001_initial.sql** — создание таблиц и индексов. Выполнить один раз при настройке Neon.

## Миграции

При добавлении новых полей или таблиц — создавать файлы 002_*.sql и т.д., обновлять описание здесь.
