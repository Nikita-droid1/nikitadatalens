"""
ETL: маржа по дням из iiko OLAP в Neon (таблица margin_iiko).
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


def get_token():
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


def fetch_margin(token, date_from, date_to, delivery_type: str):
    label = {"ALL": "ВСЕ", "COURIER": "КУРЬЕР", "PICKUP": "САМОВЫВОЗ"}[delivery_type]
    print(f"🚚 Загружаем данные 'Маржа ДМД' ({label}) из iiko...")

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
        "Storned": {"filterType": "IncludeValues", "values": ["FALSE"]},
        "DeletedWithWriteoff": {"filterType": "IncludeValues", "values": ["NOT_DELETED"]},
        "Department": {"filterType": "IncludeValues", "values": ["Авиагородок", "Домодедово"]},
        "OrderDeleted": {"filterType": "IncludeValues", "values": ["NOT_DELETED"]},
    }
    if delivery_type in ("COURIER", "PICKUP"):
        filters["Delivery.ServiceType"] = {
            "filterType": "IncludeValues",
            "values": ["COURIER" if delivery_type == "COURIER" else "PICKUP"],
        }

    body = {
        "reportType": "SALES",
        "groupByRowFields": ["Department", "OpenDate.Typed"],
        "aggregateFields": ["DishSumInt", "DiscountSum", "ProductCostBase.ProductCost"],
        "filters": filters,
    }
    resp = requests.post(url, json=body, params=params, timeout=90)
    resp.raise_for_status()
    data = resp.json()

    rows = []
    for r in data.get("data", []):
        dep = r.get("Department")
        oper_raw = r.get("OpenDate.Typed")
        if not dep or not oper_raw:
            continue
        oper_day = oper_raw[:10]
        rows.append({
            "department": dep,
            "oper_day": oper_day,
            "revenue": float(r.get("DishSumInt") or 0),
            "discount": float(r.get("DiscountSum") or 0),
            "product_cost": float(r.get("ProductCostBase.ProductCost") or 0),
        })
    print(f"📊 Получено строк ({label}): {len(rows)}")
    return rows


def upsert_base_margin(conn, rows):
    if not rows:
        print("⚠️ Нет строк для записи (ALL)")
        return
    cur = conn.cursor()
    sql = """
        INSERT INTO margin_iiko (
            department, oper_day, revenue, discount, product_cost, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, now())
        ON CONFLICT (department, oper_day)
        DO UPDATE SET
            revenue = EXCLUDED.revenue,
            discount = EXCLUDED.discount,
            product_cost = EXCLUDED.product_cost,
            updated_at = now();
    """
    for r in rows:
        cur.execute(sql, (r["department"], r["oper_day"], r["revenue"], r["discount"], r["product_cost"]))
    conn.commit()
    cur.close()
    print(f"✅ В margin_iiko записано (ALL): {len(rows)} строк")


def upsert_type_margin(conn, rows, delivery_type: str):
    if not rows:
        print(f"⚠️ Нет строк для записи ({delivery_type})")
        return
    if delivery_type == "COURIER":
        revenue_field, discount_field, cost_field = "revenue_courier", "discount_courier", "product_cost_courier"
    elif delivery_type == "PICKUP":
        revenue_field, discount_field, cost_field = "revenue_pickup", "discount_pickup", "product_cost_pickup"
    else:
        raise ValueError(f"Unknown delivery_type: {delivery_type}")

    cur = conn.cursor()
    sql = f"""
        INSERT INTO margin_iiko (
            department, oper_day, revenue, discount, product_cost,
            {revenue_field}, {discount_field}, {cost_field}, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
        ON CONFLICT (department, oper_day)
        DO UPDATE SET
            {revenue_field} = EXCLUDED.{revenue_field},
            {discount_field} = EXCLUDED.{discount_field},
            {cost_field} = EXCLUDED.{cost_field},
            updated_at = now()
    """
    for r in rows:
        cur.execute(
            sql,
            (
                r["department"], r["oper_day"],
                0.0, 0.0, 0.0,
                r["revenue"], r["discount"], r["product_cost"],
            ),
        )
    conn.commit()
    cur.close()
    print(f"✅ В margin_iiko записано ({delivery_type}): {len(rows)} строк")


def main():
    date_from, date_to = get_period()
    print(f"🚀 ETL MARGIN DAILY: {date_from} – {date_to}")

    token = get_token()
    try:
        rows_all = fetch_margin(token, date_from, date_to, "ALL")
        rows_courier = fetch_margin(token, date_from, date_to, "COURIER")
        rows_pickup = fetch_margin(token, date_from, date_to, "PICKUP")

        conn = get_pg_connection()
        try:
            upsert_base_margin(conn, rows_all)
            upsert_type_margin(conn, rows_courier, "COURIER")
            upsert_type_margin(conn, rows_pickup, "PICKUP")
        finally:
            conn.close()
            print("🔌 Соединение с Postgres закрыто")
    finally:
        logout(token)
        print("🔐 Logout выполнен")


if __name__ == "__main__":
    main()
