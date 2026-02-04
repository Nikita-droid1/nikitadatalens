# Дата-аналитика Room Broom

**Назначение:** ETL-пайплайн для выгрузки данных из iiko Server API и Google Sheets в Neon, с последующим построением дашборда в DataLens.

## Структура проекта

```
├── iiko/
│   └── api/              # Модули для работы с iiko Server API
├── google_sheets/         # Модули для работы с Google Sheets
├── neon/
│   ├── schema/           # SQL схемы БД (сырые таблицы + витрина)
│   └── transforms/       # SQL трансформации для расчета метрик
├── .github/
│   └── workflows/        # GitHub Actions для автоматизации
├── docs/                 # Документация
├── etl.py                # Главный ETL скрипт
└── requirements.txt      # Python зависимости
```

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` (пример в `.env.example`):

```bash
IIKO_BASE_URL=https://oreks-co.Iiko.it:443
IIKO_LOGIN=UKK
IIKO_PASSWORD_SHA1=2c61422714bcb5935215adf442a8f5b1d80ffc54
NEON_DATABASE_URL=postgresql://user:password@host/db?sslmode=require
GOOGLE_SHEETS_CREDENTIALS={"type": "service_account", ...}  # Опционально
```

### 3. Создание схемы БД

Выполните SQL файлы из `neon/schema/` в порядке:
1. `001_iiko_raw.sql` — таблицы для сырых данных iiko
2. `002_sheets_raw.sql` — таблицы для данных из Google Sheets
3. `003_mart.sql` — витрина данных

### 4. Запуск ETL

```bash
python etl.py
```

### 5. Обновление витрины

```bash
python neon/transforms/run_transforms.py
```

## Метрики дашборда

Дашборд включает 15 метрик:

1. Выручка по дням (доставка + самовывоз)
2. % скидки по дням (доставка + самовывоз)
3. % рекламный бюджет + ФОТ директ
4. % себестоимости (доставка + самовывоз)
5. % ФОТ курьеры
6. Потрачено руб на Упаковку (2.8% от выручки)
7. Потрачено руб на Арору (1.4% от выручки)
8. Потрачено руб на Налоги (1.1% от выручки)
9. Потрачено руб на Эквайринг (0.8% от выручки)
10. Итого маржа по дням (доставка + самовывоз)
11. ФОТ повара
12. ФОТ уборщицы
13. Нагрузка по дням и по часам по кол-ву заказов (доставка + самовывоз)
14. Нагрузка по дням и по часам по выручке (доставка + самовывоз)
15. Типы скидок по дням, количеству заказов со скидкой, выручкой с заказов со скидкой, суммой общей по скидке и среднему чеку по заказам со скидкой

## Автоматизация

GitHub Actions workflow (`daily_etl.yml`) запускается автоматически каждый день в 02:00 UTC (05:00 МСК).

Для ручного запуска: GitHub → Actions → Daily ETL → Run workflow.

## Документация

- [Документация по iiko Server API](docs/iiko-server-api.md)
- [Настройка GitHub Actions](github/README.md)
- [Настройка Neon](neon/README.md)
- [Настройка DataLens](docs/datalens_setup.md)
