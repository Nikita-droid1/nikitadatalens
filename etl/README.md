# ETL: iiko OLAP → Neon

Скрипты выгрузки отчётов iiko Server API (OLAP) в Neon. Для дашборда «Маржа» в DataLens.

**Переменные:** IIKO_BASE_URL, IIKO_LOGIN, IIKO_PASSWORD; NEON_DATABASE_URL (или PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD, PG_SSLMODE). Опционально DATE_FROM, DATE_TO (YYYY-MM-DD); по умолчанию вчера–сегодня.

| Скрипт | Таблица в Neon | Воркфлоу |
|--------|----------------|----------|
| etl_iiko_margin_daily | margin_iiko | .github/workflows/etl_iiko_margin_daily.yml |
| etl_iiko_load_hourly | load_hourly_iiko | .github/workflows/etl_iiko_load_hourly.yml |
| etl_iiko_discount_types_daily | discount_types_daily_iiko | .github/workflows/etl_iiko_discount_types_daily.yml |

**Локальный запуск:** из корня проекта `python -m etl.etl_iiko_margin_daily` (и аналогично для двух других). Перед первым запуском выполнить в Neon схемы из neon/schema/ (002, 003, 004).

**Департаменты** в коде зашиты: Авиагородок, Домодедово; при необходимости вынести в ENV.
