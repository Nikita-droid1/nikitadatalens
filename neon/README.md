# Neon: БД и постобработка

**Назначение:** база данных Postgres в Neon для хранения выгрузок из iiko и витрин под визуализацию в DataLens.

## Подключение

- Connection string — только в GitHub Secrets и в настройках подключения DataLens, не в репозитории.
- В коде и README указывать только имя переменной: `NEON_DATABASE_URL`.

## Структура

- **schema/** — таблицы. Выполнить в Neon SQL Editor один раз при настройке:
  - [001_initial.sql](schema/001_initial.sql) — iiko_raw_export (сырые JSONB), mart_sales_by_day (витрина).
  - [002_margin_iiko.sql](schema/002_margin_iiko.sql) — маржа по дням/департаментам (заполняется ETL margin).
  - [003_load_hourly_iiko.sql](schema/003_load_hourly_iiko.sql) — нагрузка по часам (заполняется ETL load_hourly).
  - [004_discount_types_daily_iiko.sql](schema/004_discount_types_daily_iiko.sql) — типы скидок по дням (заполняется ETL discount_types).
- **transforms/** — [refresh_mart.sql](transforms/refresh_mart.sql) заполняет mart_sales_by_day из iiko_raw_export; [run_transforms.py](transforms/run_transforms.py) запускает этот SQL.
- Таблицы margin_iiko, load_hourly_iiko, discount_types_daily_iiko заполняются скриптами из **etl/** (см. корневой README и .github/workflows/).

## Порядок работы

1. Скрипты из `iiko/api/` загружают сырые данные в iiko_raw_export.
2. Запуск постобработки: `python neon/transforms/run_transforms.py` (или из GitHub Action).
3. DataLens подключается к Neon и строит датасеты и дашборды по mart_sales_by_day и при необходимости по iiko_raw_export.
