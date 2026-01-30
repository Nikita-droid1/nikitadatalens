#!/usr/bin/env python3
"""
Запуск постобработки: выполнение SQL из refresh_mart.sql в Neon.
Переменная NEON_DATABASE_URL должна быть задана.
Запуск: из корня дата-аналитика: python neon/transforms/run_transforms.py
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_FILE = os.path.join(SCRIPT_DIR, "refresh_mart.sql")

def main() -> None:
    db_url = os.environ.get("NEON_DATABASE_URL")
    if not db_url:
        print("NEON_DATABASE_URL не задан.", file=sys.stderr)
        sys.exit(1)
    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql = f.read()
    # Выполняем весь скрипт (один блок: CTE + INSERT)
    block = sql.split("-- Вариант 2:")[0].strip() if "-- Вариант 2:" in sql else sql.strip()
    if not block:
        print("Нет выполняемого блока в refresh_mart.sql.", file=sys.stderr)
        sys.exit(1)
    import psycopg2
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(block)
        print("Постобработка выполнена: mart_sales_by_day обновлена.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
