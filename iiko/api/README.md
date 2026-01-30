# Скрипты вызова iiko API

**Назначение:** код для запроса данных с iiko API и передачи их в Neon (или сохранения в JSON).

## Скрипты

- **client.py** — клиент iiko Cloud API: `get_access_token()`, `get_organizations()`, `get_delivery_report(from_date, to_date)`.
- **run_export.py** — основной скрипт: выгрузка за последние 7 дней (эндпоинт `/api/1/deliveries/by_delivery_date_and_status`), сохранение в `iiko/api/out/` и запись в Neon (таблица `iiko_raw_export`).

## Как запускать

**Локально (из корня дата-аналитика):**
```bash
pip install -r requirements.txt
cp .env.example .env   # заполнить значения
python -m iiko.api.run_export
```

**Из GitHub Actions** — через workflow из [github/workflows/](../../github/workflows/); секреты задаются в GitHub Secrets.
