# Постобработка данных для DataLens

**Назначение:** SQL и скрипт, которые из iiko_raw_export заполняют витрину mart_sales_by_day для DataLens.

## Файлы

- **refresh_mart.sql** — SQL: вставка/обновление mart_sales_by_day из payload в iiko_raw_export. Структура JSONB в комментариях; при расхождении с вашим API скорректируйте пути (payload->'deliveries', payload->'orders' и т.д.).
- **run_transforms.py** — запуск первого блока refresh_mart.sql в Neon (требуется NEON_DATABASE_URL).

## Запуск

- **Вручную:** из корня дата-аналитика: `python neon/transforms/run_transforms.py` (нужен .env с NEON_DATABASE_URL).
- **Из GitHub Action:** после шага выгрузки из iiko вызвать этот скрипт в том же workflow.
