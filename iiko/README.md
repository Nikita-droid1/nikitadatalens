# iiko Server (Resto) API

**Назначение:** выгрузка данных по ресторанам с iiko через iiko Server (Resto) API. Документация: [docs/iiko-server-api.md](../docs/iiko-server-api.md).

## Что выгружаем

Эндпоинты и формат ответов — по [docs/iiko-server-api.md](../docs/iiko-server-api.md) и ru.iiko.help. После перехода клиента на Resto API здесь будет актуальный список методов (организации, склады, отчёты/заказы и т.д.). При расхождении ответов скорректируйте [api/client.py](api/client.py) и [neon/transforms/refresh_mart.sql](../neon/transforms/refresh_mart.sql).

## Авторизация и конфиг

- **IIKO_BASE_URL** — базовый URL сервера iiko (например `https://oreks-co.iiko.it:443`).
- **IIKO_LOGIN** — логин пользователя API.
- **IIKO_PASSWORD_SHA1** — SHA1-хеш пароля (не сам пароль). Либо **IIKO_PASSWORD** и хеширование в коде.
- **NEON_DATABASE_URL** — connection string Neon (опционально для локального запуска без записи в БД).
- Локальный тест: скопировать [../.env.example](../.env.example) в `.env` в корне дата-аналитика, подставить значения. Файл `.env` в `.gitignore`.

## Структура

- **api/client.py** — клиент: авторизация (GET /resto/api/auth), запросы к Resto API (после перехода на Resto).
- **api/run_export.py** — основной скрипт: выгрузка, сохранение в JSON и запись в Neon (если задан NEON_DATABASE_URL).
