# Справочник: репозиторий iiko-etl (от коллеги)

**Назначение:** зафиксировать структуру и пайплайны из репозитория коллеги (`iiko-etl`), чтобы использовать при дальнейшей работе с дата-аналитикой и ETL.

---

## Расположение

- Папка от коллеги: `~/Downloads/iiko-etl.-main` (или клон репозитория).

---

## Воркфлоу (GitHub Actions)

| Файл | Запуск | Назначение |
|------|--------|------------|
| `iiko_load_hourly.yml` | 06:00 МСК ежедневно + ручной | OLAP «Нагрузка по часам» → таблица `load_hourly_iiko` (PG_*) |
| `iiko_crm_daily.yml` | 07:00 МСК ежедневно + ручной | Отчёт для CRM (reportId) → Neon CRM (PG_CRM_*) |
| `iiko_t1_light.yml` | ручной | T1 Light → основная Postgres (PG_*) |
| `iiko_t1_light_crm.yml` | ручной | T1 Light → Neon CRM (PG_CRM_*) |
| `iiko_margin_daily.yml` | 07:00 МСК ежедневно + ручной | Маржа по дням → PG_* |
| `discount_types_daily.yml` | — | Типы скидок по дням |
| `stock_tx_daily.yml` | — | Складские движения по дням |
| `fot_daily.yml` | 13:00 МСК ежедневно | Google Sheets (FOT) → PG_* |
| `fot_daily_crm.yml` | — | Google Sheets (FOT) → PG_CRM_* |

---

## Python-скрипты (ETL)

- **etl_iiko_load_hourly.py** — OLAP `/api/v2/reports/olap`, SALES, группировка по дню/часу/департаменту; upsert в `load_hourly_iiko`.
- **etl_iiko_crm_daily.py** — отчёт CRM по reportId → PG_CRM_*.
- **etl_iiko_t1_light.py** / **etl_iiko_t1_light_crm.py** — T1 Light в PG_* и PG_CRM_*.
- **etl_iiko_margin_daily.py** — маржа по дням.
- **etl_iiko_discount_types_daily.py** — типы скидок.
- **etl_iiko_stock_tx_daily.py** — складские операции.
- **etl_fot_daily.py** / **etl_fot_daily_crm.py** — данные из Google Sheets (FOT) в PG_* и PG_CRM_*.

---

## Авторизация iiko

- **iiko Server API** (не iikoCloud): `GET {IIKO_BASE_URL}/api/auth?login=&pass=` — пароль в открытом виде; ответ — текст токена.
- Дальше запросы с `key=token`; по окончании — `POST /api/logout?key=token`.

---

## Переменные окружения / секреты

**iiko (общие):** `IIKO_BASE_URL`, `IIKO_LOGIN`, `IIKO_PASSWORD`.

**Основная Postgres (Neon):** `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASSWORD`, `PG_SSLMODE` (require).

**Neon CRM (отдельный проект):** `PG_CRM_HOST`, `PG_CRM_PORT`, `PG_CRM_DB`, `PG_CRM_USER`, `PG_CRM_PASSWORD`, `PG_CRM_SSLMODE`.

**FOT (Google Sheets):** `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS`.

**Период (опционально):** `DATE_FROM`, `DATE_TO` (YYYY-MM-DD); если пусто — часто «вчера → сегодня».

---

## Жёстко зашито в коде (при переносе править под себя)

- **etl_iiko_load_hourly.py:** `DEPARTMENTS = ["Авиагородок", "Домодедово"]`; типы заказов — доставка/самовывоз.
- **etl_iiko_crm_daily.py:** `REPORT_ID = "1df51370-2567-40c3-8cbf-b32f966125bd"` — отчёт для CRM; может отличаться в другом iiko.

---

## Зависимости (requirements.txt)

`requests`, `python-dotenv`, `psycopg2-binary`, `gspread`, `google-auth`.

---

При интеграции с этим репозиторием, переносе пайплайнов в `Работа/1_дата-аналитика` или настройке новых ETL — опираться на этот справочник.
