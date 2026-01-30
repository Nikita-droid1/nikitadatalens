# GitHub: код и триггеры выгрузки

**Назначение:** хранение кода выгрузки из iiko, ручной запуск выгрузки через Actions, настройка секретов.

## Важно: секреты

- Логины, пароли и API-ключи **не коммитить** в репозиторий.
- Использовать **GitHub Secrets**: Settings → Secrets and variables → Actions.
- В коде — только обращение к переменным окружения: `IIKO_BASE_URL`, `IIKO_LOGIN`, `IIKO_PASSWORD` или `IIKO_PASSWORD_SHA1`, `NEON_DATABASE_URL`.

## Workflow

- В корне дата-аналитика: **.github/workflows/export-iiko.yml** — ручная выгрузка по кнопке (workflow_dispatch).
- Копия для справки: **workflows/export-iiko.yml**.
- Запуск: GitHub → Actions → «Export iiko to Neon» → Run workflow.
- Если корень репозитория — не дата-аналитика, а родительская папка: скопировать export-iiko.yml в .github/workflows в корне репо и в шагах перейти в папку дата-аналитика (например `working-directory: Работа/дата-аналитика`).

## Секреты для workflow

| Секрет | Назначение |
|--------|------------|
| IIKO_BASE_URL | Базовый URL сервера iiko (например https://oreks-co.iiko.it:443) |
| IIKO_LOGIN | Логин пользователя API |
| IIKO_PASSWORD или IIKO_PASSWORD_SHA1 | Пароль в открытом виде или SHA1-хеш (зависит от сервера) |
| NEON_DATABASE_URL | Connection string Neon (postgresql://user:password@host/db?sslmode=require) |

**Как заполнить секреты в GitHub**

1. Открой репозиторий → вкладка **Settings** → слева **Secrets and variables** → **Actions**.
2. Нажми **New repository secret** и по очереди создай четыре секрета:

| Имя секрета (вводить точно) | Значение (что вставить) |
|-----------------------------|--------------------------|
| **IIKO_BASE_URL** | Адрес сервера iiko, например `https://oreks-co.iiko.it:443` (без слэша в конце). |
| **IIKO_LOGIN** | Логин пользователя API (тот же, что у коллеги в коде). |
| **IIKO_PASSWORD** | Пароль в открытом виде (если сервер принимает обычный пароль, как у коллеги). Либо создай **IIKO_PASSWORD_SHA1** и вставь туда SHA1-хеш пароля — нужен только один из двух. |
| **NEON_DATABASE_URL** | Строка подключения к Neon из консоли Neon: `postgresql://user:password@host/dbname?sslmode=require`. |

3. Имя секрета копируй из таблицы без пробелов; значение вставляй без кавычек. После сохранения значение не показывается — только звёздочки.
4. Для выгрузки из iiko достаточно секретов IIKO_* и NEON_DATABASE_URL. После добавления запускай workflow: **Actions** → «Export iiko to Neon» → **Run workflow**.
