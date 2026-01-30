# GitHub Actions workflows

**Назначение:** автоматизация выгрузки данных из iiko по кнопке (и при необходимости по расписанию).

## Workflows

- **export-iiko.yml** — ручная выгрузка (workflow_dispatch): запуск вручную из Actions → «Export iiko to Neon» → Run workflow. Выполняет `iiko.api.run_export` и `neon/transforms/run_transforms.py`.
- **По расписанию** (опционально): добавить в on: schedule: cron при необходимости регулярной синхронизации.

## Файлы

- **export-iiko.yml** — копия рабочего workflow (основной файл в .github/workflows/ в корне дата-аналитика).
