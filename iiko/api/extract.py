"""
Основной ETL скрипт для выгрузки данных из iiko Server API в Neon.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .auth import get_token
from .olap_reports import (
    get_margin_report,
    get_load_orders_report,
    get_load_revenue_report,
    get_discount_types_report
)


def get_db_connection():
    """Получить подключение к Neon."""
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def parse_margin_report(data: Dict[str, Any]) -> list:
    """
    Парсинг отчета "Маржа" и преобразование в формат для БД.
    
    Структура данных может отличаться в зависимости от формата ответа API.
    Нужно будет адаптировать под реальный формат.
    """
    rows = []
    
    # Предполагаем, что данные приходят в виде массива строк отчета
    # Точная структура зависит от формата ответа iiko API
    if isinstance(data, dict):
        # Если данные в формате JSON с полями
        if "rows" in data:
            for row in data["rows"]:
                rows.append({
                    "report_date": row.get("OpenDate.Typed") or row.get("date"),
                    "department": row.get("Department") or row.get("department"),
                    "dish_sum_int": row.get("DishSumInt") or row.get("dish_sum_int"),
                    "discount_sum": row.get("DiscountSum") or row.get("discount_sum"),
                    "product_cost_base_percent": row.get("ProductCostBase.Percent") or row.get("cost_percent"),
                    "raw_data": json.dumps(row)
                })
        else:
            # Альтернативный формат - плоская структура
            rows.append({
                "report_date": data.get("date") or data.get("OpenDate.Typed"),
                "department": data.get("Department") or data.get("department"),
                "dish_sum_int": data.get("DishSumInt") or data.get("dish_sum_int"),
                "discount_sum": data.get("DiscountSum") or data.get("discount_sum"),
                "product_cost_base_percent": data.get("ProductCostBase.Percent") or data.get("cost_percent"),
                "raw_data": json.dumps(data)
            })
    elif isinstance(data, list):
        for item in data:
            rows.append({
                "report_date": item.get("date") or item.get("OpenDate.Typed"),
                "department": item.get("Department") or item.get("department"),
                "dish_sum_int": item.get("DishSumInt") or item.get("dish_sum_int"),
                "discount_sum": item.get("DiscountSum") or item.get("discount_sum"),
                "product_cost_base_percent": item.get("ProductCostBase.Percent") or item.get("cost_percent"),
                "raw_data": json.dumps(item)
            })
    
    return rows


def parse_load_orders_report(data: Dict[str, Any]) -> list:
    """Парсинг отчета "Нагрузка по часам (заказы)"."""
    rows = []
    
    # Аналогично parse_margin_report, адаптируем под реальный формат
    if isinstance(data, dict):
        if "rows" in data:
            for row in data["rows"]:
                rows.append({
                    "report_date": row.get("OpenDate.Typed") or row.get("date"),
                    "department": row.get("Department") or row.get("department"),
                    "hour_open": row.get("HourOpen") or row.get("hour"),
                    "orders_count": row.get("UniqOrderId.OrdersCount") or row.get("orders_count"),
                    "raw_data": json.dumps(row)
                })
        else:
            rows.append({
                "report_date": data.get("date") or data.get("OpenDate.Typed"),
                "department": data.get("Department") or data.get("department"),
                "hour_open": data.get("HourOpen") or data.get("hour"),
                "orders_count": data.get("UniqOrderId.OrdersCount") or data.get("orders_count"),
                "raw_data": json.dumps(data)
            })
    elif isinstance(data, list):
        for item in data:
            rows.append({
                "report_date": item.get("date") or item.get("OpenDate.Typed"),
                "department": item.get("Department") or item.get("department"),
                "hour_open": item.get("HourOpen") or item.get("hour"),
                "orders_count": item.get("UniqOrderId.OrdersCount") or item.get("orders_count"),
                "raw_data": json.dumps(item)
            })
    
    return rows


def parse_load_revenue_report(data: Dict[str, Any]) -> list:
    """Парсинг отчета "Нагрузка по часам (выручка)"."""
    rows = []
    
    if isinstance(data, dict):
        if "rows" in data:
            for row in data["rows"]:
                rows.append({
                    "report_date": row.get("OpenDate.Typed") or row.get("date"),
                    "department": row.get("Department") or row.get("department"),
                    "hour_open": row.get("HourOpen") or row.get("hour"),
                    "dish_discount_sum_int": row.get("DishDiscountSumInt") or row.get("revenue"),
                    "raw_data": json.dumps(row)
                })
        else:
            rows.append({
                "report_date": data.get("date") or data.get("OpenDate.Typed"),
                "department": data.get("Department") or data.get("department"),
                "hour_open": data.get("HourOpen") or data.get("hour"),
                "dish_discount_sum_int": data.get("DishDiscountSumInt") or data.get("revenue"),
                "raw_data": json.dumps(data)
            })
    elif isinstance(data, list):
        for item in data:
            rows.append({
                "report_date": item.get("date") or item.get("OpenDate.Typed"),
                "department": item.get("Department") or item.get("department"),
                "hour_open": item.get("HourOpen") or item.get("hour"),
                "dish_discount_sum_int": item.get("DishDiscountSumInt") or item.get("revenue"),
                "raw_data": json.dumps(item)
            })
    
    return rows


def parse_discount_types_report(data: Dict[str, Any]) -> list:
    """Парсинг отчета "Типы скидок"."""
    rows = []
    
    if isinstance(data, dict):
        if "rows" in data:
            for row in data["rows"]:
                rows.append({
                    "report_date": row.get("OpenDate.Typed") or row.get("date"),
                    "department": row.get("Department") or row.get("department"),
                    "discount_type": row.get("OrderDiscount.Type") or row.get("discount_type"),
                    "orders_count": row.get("UniqOrderId.OrdersCount") or row.get("orders_count"),
                    "dish_discount_sum_int": row.get("DishDiscountSumInt") or row.get("revenue"),
                    "discount_sum": row.get("DiscountSum") or row.get("discount_sum"),
                    "average_order_sum": row.get("DishDiscountSumInt.average") or row.get("average_check"),
                    "raw_data": json.dumps(row)
                })
        else:
            rows.append({
                "report_date": data.get("date") or data.get("OpenDate.Typed"),
                "department": data.get("Department") or data.get("department"),
                "discount_type": data.get("OrderDiscount.Type") or data.get("discount_type"),
                "orders_count": data.get("UniqOrderId.OrdersCount") or data.get("orders_count"),
                "dish_discount_sum_int": data.get("DishDiscountSumInt") or data.get("revenue"),
                "discount_sum": data.get("DiscountSum") or data.get("discount_sum"),
                "average_order_sum": data.get("DishDiscountSumInt.average") or data.get("average_check"),
                "raw_data": json.dumps(data)
            })
    elif isinstance(data, list):
        for item in data:
            rows.append({
                "report_date": item.get("date") or item.get("OpenDate.Typed"),
                "department": item.get("Department") or item.get("department"),
                "discount_type": item.get("OrderDiscount.Type") or item.get("discount_type"),
                "orders_count": item.get("UniqOrderId.OrdersCount") or item.get("orders_count"),
                "dish_discount_sum_int": item.get("DishDiscountSumInt") or item.get("revenue"),
                "discount_sum": item.get("DiscountSum") or item.get("discount_sum"),
                "average_order_sum": item.get("DishDiscountSumInt.average") or item.get("average_check"),
                "raw_data": json.dumps(item)
            })
    
    return rows


def load_margin_report(date_from: datetime, date_to: datetime, token: Optional[str] = None):
    """Загрузить отчет "Маржа" в БД."""
    print(f"📊 Загрузка отчета 'Маржа' за период {date_from.date()} - {date_to.date()}")
    
    # Получаем данные из API
    data = get_margin_report(date_from, date_to, token)
    
    # Парсим данные
    rows = parse_margin_report(data)
    
    if not rows:
        print("⚠️  Нет данных для загрузки")
        return
    
    # Загружаем в БД
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO iiko_raw_margin 
            (report_date, department, dish_sum_int, discount_sum, product_cost_base_percent, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department) 
            DO UPDATE SET
                dish_sum_int = EXCLUDED.dish_sum_int,
                discount_sum = EXCLUDED.discount_sum,
                product_cost_base_percent = EXCLUDED.product_cost_base_percent,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["dish_sum_int"],
                    row["discount_sum"],
                    row["product_cost_base_percent"],
                    row["raw_data"]
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def load_load_orders_report(date_from: datetime, date_to: datetime, token: Optional[str] = None):
    """Загрузить отчет "Нагрузка по часам (заказы)" в БД."""
    print(f"📊 Загрузка отчета 'Нагрузка по часам (заказы)' за период {date_from.date()} - {date_to.date()}")
    
    data = get_load_orders_report(date_from, date_to, token)
    rows = parse_load_orders_report(data)
    
    if not rows:
        print("⚠️  Нет данных для загрузки")
        return
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO iiko_raw_load_orders 
            (report_date, department, hour_open, orders_count, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department, hour_open) 
            DO UPDATE SET
                orders_count = EXCLUDED.orders_count,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["hour_open"],
                    row["orders_count"],
                    row["raw_data"]
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def load_load_revenue_report(date_from: datetime, date_to: datetime, token: Optional[str] = None):
    """Загрузить отчет "Нагрузка по часам (выручка)" в БД."""
    print(f"📊 Загрузка отчета 'Нагрузка по часам (выручка)' за период {date_from.date()} - {date_to.date()}")
    
    data = get_load_revenue_report(date_from, date_to, token)
    rows = parse_load_revenue_report(data)
    
    if not rows:
        print("⚠️  Нет данных для загрузки")
        return
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO iiko_raw_load_revenue 
            (report_date, department, hour_open, dish_discount_sum_int, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department, hour_open) 
            DO UPDATE SET
                dish_discount_sum_int = EXCLUDED.dish_discount_sum_int,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["hour_open"],
                    row["dish_discount_sum_int"],
                    row["raw_data"]
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def load_discount_types_report(date_from: datetime, date_to: datetime, token: Optional[str] = None):
    """Загрузить отчет "Типы скидок" в БД."""
    print(f"📊 Загрузка отчета 'Типы скидок' за период {date_from.date()} - {date_to.date()}")
    
    data = get_discount_types_report(date_from, date_to, token)
    rows = parse_discount_types_report(data)
    
    if not rows:
        print("⚠️  Нет данных для загрузки")
        return
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO iiko_raw_discount_types 
            (report_date, department, discount_type, orders_count, dish_discount_sum_int, 
             discount_sum, average_order_sum, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department, discount_type) 
            DO UPDATE SET
                orders_count = EXCLUDED.orders_count,
                dish_discount_sum_int = EXCLUDED.dish_discount_sum_int,
                discount_sum = EXCLUDED.discount_sum,
                average_order_sum = EXCLUDED.average_order_sum,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["discount_type"],
                    row["orders_count"],
                    row["dish_discount_sum_int"],
                    row["discount_sum"],
                    row["average_order_sum"],
                    row["raw_data"]
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def run_iiko_etl(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    """
    Запустить полный ETL процесс для всех отчетов iiko.
    
    Args:
        date_from: Дата начала периода (по умолчанию - вчера)
        date_to: Дата окончания периода (по умолчанию - вчера)
    """
    if date_from is None:
        date_from = datetime.now() - timedelta(days=1)
    if date_to is None:
        date_to = datetime.now() - timedelta(days=1)
    
    # Получаем токен один раз для всех запросов
    token = get_token()
    
    try:
        # Загружаем все отчеты
        load_margin_report(date_from, date_to, token)
        load_load_orders_report(date_from, date_to, token)
        load_load_revenue_report(date_from, date_to, token)
        load_discount_types_report(date_from, date_to, token)
        
        print("✅ ETL процесс завершен успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении ETL: {e}")
        raise


if __name__ == "__main__":
    # Запуск ETL для вчерашнего дня
    run_iiko_etl()
