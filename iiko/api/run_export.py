#!/usr/bin/env python3
"""
Скрипт выгрузки данных из iiko API и загрузки в Neon.
Запуск: из корня дата-аналитика или из iiko/api с установленным PYTHONPATH.
Переменные: IIKO_BASE_URL (или IIKO_API_URL), IIKO_LOGIN (или IIKO_API_LOGIN), IIKO_PASSWORD_SHA1 для Resto; NEON_DATABASE_URL (опционально). См. docs/iiko-server-api.md.
"""

import json
import os
import sys
from datetime import datetime, timedelta

# Корень проекта дата-аналитика (родитель папки iiko)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from iiko.api.client import IikoClient  # noqa: E402


def load_to_neon(raw_json: dict, table_raw: str = "iiko_raw_export") -> None:
    """Записать сырой ответ API в Neon (таблица с JSONB)."""
    db_url = os.environ.get("NEON_DATABASE_URL")
    if not db_url:
        print("NEON_DATABASE_URL не задан — пропуск записи в БД.")
        return
    import psycopg2
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS iiko_raw_export (
                    id SERIAL PRIMARY KEY,
                    exported_at TIMESTAMPTZ DEFAULT NOW(),
                    payload JSONB NOT NULL
                )
                """
            )
            cur.execute(
                "INSERT INTO iiko_raw_export (payload) VALUES (%s)",
                (json.dumps(raw_json, ensure_ascii=False),),
            )
        conn.commit()
        print("Данные записаны в Neon, таблица iiko_raw_export.")
    finally:
        conn.close()


def main() -> None:
    # Период по умолчанию — последние 7 дней (формат API: yyyy-MM-dd HH:mm:ss.fff)
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=7)
    delivery_from = f"{from_date.isoformat()} 00:00:00.000"
    delivery_to = f"{to_date.isoformat()} 23:59:59.999"

    client = IikoClient()
    print("Получение организаций...")
    orgs = client.get_organizations()
    print(f"Организаций: {len(orgs)}")

    print("Запрос заказов по дате доставки...")
    try:
        report = client.get_orders_by_delivery_date(delivery_from, delivery_to)
        print("Заказы получены.")
    except Exception as e:
        print(f"Заказы по дате недоступны ({e}); сохраняем только организации.")
        report = {"organizations": orgs, "deliveryDateFrom": delivery_from, "deliveryDateTo": delivery_to, "error": str(e)}

    # Сохранить в файл для отладки (опционально)
    out_dir = os.path.join(PROJECT_ROOT, "iiko", "api", "out")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"orders_{from_date.isoformat()}_{to_date.isoformat()}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Сохранено в файл: {out_file}")

    load_to_neon(report)


if __name__ == "__main__":
    main()
