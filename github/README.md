# GitHub: код и автоматизация ETL

**Назначение:** автоматический ежедневный запуск ETL процесса через GitHub Actions.

## Где хранятся учётные данные

| Где | Файл/место | Когда нужны |
|-----|-------------|-------------|
| **Локально** | `.env` в корне проекта (не коммитится) | Запуск скриптов на своей машине |
| **GitHub Actions** | Settings → Secrets and variables → Actions | Автоматический запуск workflow (ETL, выгрузка) |

**Напоминание:** при настройке GitHub Actions добавь в Secrets: `IIKO_BASE_URL`, `IIKO_LOGIN`, `IIKO_PASSWORD_SHA1`. Значения бери из своего локального `.env`.

## Workflow

- **`.github/workflows/daily_etl.yml`** — ручной запуск ETL через кнопку
- Запуск: GitHub → Actions → «ETL (ручной запуск)» → Run workflow → Run workflow
- Автоматический запуск по расписанию отключен (только ручной запуск)

## Секреты для workflow

| Секрет | Назначение |
|--------|------------|
| `IIKO_BASE_URL` | Базовый URL сервера iiko (например https://oreks-co.Iiko.it:443) |
| `IIKO_LOGIN` | Логин пользователя API (UKK) |
| `IIKO_PASSWORD_SHA1` | SHA1-хеш пароля пользователя API |
| `NEON_DATABASE_URL` | Connection string Neon (postgresql://user:password@host/db?sslmode=require) |
| `GOOGLE_SHEETS_CREDENTIALS` | JSON credentials сервисного аккаунта Google (опционально, если не используется — загрузка из Google Sheets пропускается) |

**Как добавить:** Репозиторий → Settings → Secrets and variables → Actions → New repository secret.

## Что делает workflow

1. Устанавливает Python и зависимости из `requirements.txt`
2. Запускает `etl.py` — загружает данные из iiko API и Google Sheets в Neon
3. Запускает `neon/transforms/run_transforms.py` — обновляет витрину данных с расчетом всех метрик
4. При ошибке выводит сообщение (можно добавить уведомления)

## Как запустить вручную

1. Откройте репозиторий на GitHub
2. Перейдите во вкладку **Actions**
3. В списке слева выберите **"ETL (ручной запуск)"**
4. Нажмите кнопку **"Run workflow"** (справа)
5. Выберите ветку (обычно `main`) и нажмите **"Run workflow"**
6. Дождитесь завершения (обычно 1-2 минуты)
7. Проверьте логи на наличие ошибок
