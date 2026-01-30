"""
ETL: нагрузка по часам из iiko OLAP в Neon (таблица load_hourly_iiko).
Секреты: IIKO_BASE_URL, IIKO_LOGIN, IIKO_PASSWORD; NEON_DATABASE_URL или PG_*.
Опционально: DATE_FROM, DATE_TO (YYYY-MM-DD); по умолчанию вчера–сегодня.
"""
import os
import datetime as dt
import requests
from dotenv import load_dotenv

load_dotenv()

from etl.pg_connection import get_pg_connection

IIKO_BASE_URL = os.getenv("IIKO_BASE_URL", "").rstrip("/")
IIKO_LOGIN = os.getenv("IIKO_LOGIN")
IIKO_PASSWORD = os.getenv("IIKO_PASSWORD")

DEPARTMENTS = ["Авиагородок", "Домодедово"]
ORDER_TYPES = ["Delivery by courier", "Доставка самовывоз"]


def get_period():
    date_from_str = os.getenv("DATE_FROM")
    date_to_str = os.getenv("DATE_TO")
    if date_from_str and date_to_str:
        date_from = dt.date.fromisoformat(date_from_str)
        date_to = dt.date.fromisoformat(date_to_str)
        print(f"📅 Используем период из ENV: {date_from} – {date_to}")
        return date_from, date_to
    today = dt.date.today()
    date_from = today - dt.timedelta(days=1)
    date_to = today
    print(f"📅 Используем период по умолчанию: {date_from} – {date_to}")
    return date_from, date_to


def get_token() -> str:
    url = f"{IIKO_BASE_URL}/api/auth"
    params = {"login": IIKO_LOGIN, "pass": IIKO_PASSWORD}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    token = resp.text.strip()
    print(f"🔑 Токен получен: {token[:6]}...")
    return token


def logout(token: str):
    url = f"{IIKO_BASE_URL}/api/logout"
    params = {"key": token}
    try:
        requests.post(url, params=params, timeout=10)
    except Exception as e:
        print("⚠️ Ошибка при logout:", e)


def _safe_int_hour(v) -> int:
    s = str(v).strip() if v is not None else ""
    num = ""
    for ch in s:
        if ch.isdigit():
            num += ch
        else:
            break
    return int(num) if num else 0


def fetch_load_hourly(token: str, date_from: dt.date, date_to: dt.date):
    print("📊 Загружаем OLAP 'Нагрузка по часам' из iiko...")
    url = f"{IIKO_BASE_URL}/api/v2/reports/olap"
    params = {"key": token}
    filters = {
        "OpenDate.Typed": {
            "filterType": "DateRange",
            "periodType": "CUSTOM",
            "from": date_from.strftime("%Y-%m-%d"),
            "to": date_to.strftime("%Y-%m-%d"),
            "includeLow": True,
            "includeHigh": False,
        },
        "DeletedWithWriteoff": {"filterType": "IncludeValues", "values": ["NOT_DELETED"]},
        "OrderDeleted": {"filterType": "IncludeValues", "values": ["NOT_DELETED"]},
        "Storned": {"filterType": "IncludeValues", "values": ["FALSE"]},
        "OrderType": {"filterType": "IncludeValues", "values": ORDER_TYPES},
        "Department": {"filterType": "IncludeValues", "values": DEPARTMENTS},
    }
    body = {
        "reportType": "SALES",
        "groupByRowFields": ["OpenDate.Typed", "HourOpen", "Department"],
        "aggregateFields": ["UniqOrderId.OrdersCount", "DishSumInt", "DiscountSum"],
        "filters": filters,
    }
    resp = requests.post(url, json=body, params=params, timeout=120)
    if resp.status_code != 200:
        print(f"❌ HTTP статус iiko: {resp.status_code}")
        print(resp.text[:500])
        resp.raise_for_status()
    data = resp.json()

    out = []
    for r in data.get("data", []):
        dep = r.get("Department")
        oper = r.get("OpenDate.Typed")
        hour_raw = r.get("HourOpen")
        if dep is None or oper is None or hour_raw is None:
            continue
        oper_day = str(oper)[:10]
        hour = _safe_int_hour(hour_raw)
        out.append({
            "department": str(dep),
            "oper_day": oper_day,
            "hour": hour,
            "orders_count": int(float(r.get("UniqOrderId.OrdersCount") or 0)),
            "revenue": float(r.get("DishSumInt") or 0),
            "discount": float(r.get("DiscountSum") or 0),
        })
    print(f"✅ Получено строк: {len(out)}")
    return out


UPSERT_SQL = """
INSERT INTO load_hourly_iiko (
    department, oper_day, hour, orders_count, revenue, discount
)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (department, oper_day, hour)
DO UPDATE SET
    orders_count = EXCLUDED.orders_count,
    revenue      = EXCLUDED.revenue,
    discount     = EXCLUDED.discount,
    updated_at   = now();
"""


def upsert_rows(conn, rows):
    if not rows:
        print("⚠️ Нет строк для записи")
        return
    with conn.cursor() as cur:
        for r in rows:
            cur.execute(
                UPSERT_SQL,
                (r["department"], r["oper_day"], r["hour"], r["orders_count"], r["revenue"], r["discount"]),
            )
    conn.commit()
    print(f"💾 В load_hourly_iiko upsert'нуто строк: {len(rows)}")


def main():
    date_from, date_to = get_period()
    print(f"🚀 ETL LOAD HOURLY: {date_from} – {date_to}")
    token = get_token()
    try:
        rows = fetch_load_hourly(token, date_from, date_to)
        conn = get_pg_connection()
        try:
            upsert_rows(conn, rows)
        finally:
            conn.close()
            print("🔌 Соединение с Postgres закрыто")
    finally:
        logout(token)
        print("🔐 Logout выполнен")


if __name__ == "__main__":
    main()
