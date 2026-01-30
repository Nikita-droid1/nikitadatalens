# Документация проекта

**Назначение:** справочные материалы по API и сервисам, используемым в дата-аналитике.

## Файлы

- **iiko-server-api.md** — документация по iiko Server (Resto) API: авторизация (GET /resto/api/auth, логин + SHA1 пароля), лицензия, ссылки на ru.iiko.help и [iikophpserverapi.readme.io](https://iikophpserverapi.readme.io/docs). Используется при доработке [iiko/api/](../iiko/api/) и [neon/transforms/](../neon/transforms/).

## Связь с кодом

- Клиент и скрипты выгрузки: [iiko/api/](../iiko/api/) — авторизация и вызовы Resto API (эндпоинты уточняются по [iiko-server-api.md](iiko-server-api.md) и ru.iiko.help).
- Постобработка: [neon/transforms/refresh_mart.sql](../neon/transforms/refresh_mart.sql) — разбор payload зависит от формата ответа iiko Server (Resto); при смене API адаптировать пути JSONB под реальный ответ.
