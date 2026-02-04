"""
Загрузка данных из Google Sheets в Neon.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .extract import (
    extract_direct_data,
    extract_fot_data,
    get_direct_data_by_date_range,
    get_fot_data_by_date_range
)


def get_db_connection():
    """Получить подключение к Neon."""
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def normalize_department_name(dept: str) -> str:
    """
    Нормализовать название торгового предприятия.
    
    Приводит к стандартному формату: "Домодедово" или "Авиагородок"
    """
    dept_lower = dept.strip().lower()
    
    if "домодедово" in dept_lower or "филиал 2" in dept_lower:
        return "Домодедово"
    elif "авиагородок" in dept_lower or "филиал 1" in dept_lower:
        return "Авиагородок"
    
    return dept.strip()


def load_direct_data(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    """
    Загрузить данные из таблицы "Директ" в БД.
    
    Args:
        date_from: Дата начала периода (если None, загружаются все данные)
        date_to: Дата окончания периода (если None, загружаются все данные)
    """
    print("📊 Загрузка данных из таблицы 'Директ'")
    
    # Получаем данные из Google Sheets
    if date_from and date_to:
        df = get_direct_data_by_date_range(date_from, date_to)
    else:
        df = extract_direct_data()
    
    if df.empty:
        print("⚠️  Нет данных для загрузки")
        return
    
    # Подготавливаем данные для вставки
    rows = []
    for _, row in df.iterrows():
        # Ищем колонки (могут быть разные названия)
        date_col = None
        ad_budget_col = None
        fot_col = None
        dept_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if "дата" in col_lower:
                date_col = col
            elif "реклам" in col_lower or "бюджет" in col_lower:
                ad_budget_col = col
            elif "фот" in col_lower and "директ" in col_lower:
                fot_col = col
            elif "торгов" in col_lower or "предприят" in col_lower or "филиал" in col_lower:
                dept_col = col
        
        if not date_col:
            print("⚠️  Не найдена колонка с датой")
            continue
        
        report_date = row[date_col]
        if pd.isna(report_date):
            continue
        
        # Преобразуем дату
        if isinstance(report_date, str):
            try:
                report_date = datetime.strptime(report_date, "%d.%m.%Y").date()
            except:
                continue
        
        department = normalize_department_name(row.get(dept_col, ""))
        ad_budget = float(row.get(ad_budget_col, 0) or 0)
        fot_direct = float(row.get(fot_col, 0) or 0)
        
        rows.append({
            "report_date": report_date,
            "department": department,
            "ad_budget": ad_budget,
            "fot_direct": fot_direct,
            "raw_data": row.to_dict()
        })
    
    if not rows:
        print("⚠️  Нет валидных данных для загрузки")
        return
    
    # Загружаем в БД
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO sheets_raw_direct 
            (report_date, department, ad_budget, fot_direct, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department) 
            DO UPDATE SET
                ad_budget = EXCLUDED.ad_budget,
                fot_direct = EXCLUDED.fot_direct,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["ad_budget"],
                    row["fot_direct"],
                    json.dumps(row["raw_data"])
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def load_fot_data(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    """
    Загрузить данные ФОТ (курьеры, повара, уборщицы) в БД.
    
    Args:
        date_from: Дата начала периода (если None, загружаются все данные)
        date_to: Дата окончания периода (если None, загружаются все данные)
    """
    print("📊 Загрузка данных ФОТ")
    
    # Получаем данные из Google Sheets
    if date_from and date_to:
        df = get_fot_data_by_date_range(date_from, date_to)
    else:
        df = extract_fot_data()
    
    if df.empty:
        print("⚠️  Нет данных для загрузки")
        return
    
    # Подготавливаем данные для вставки
    rows = []
    for _, row in df.iterrows():
        # Ищем колонки
        date_col = None
        fot_couriers_col = None
        fot_cooks_col = None
        fot_cleaners_col = None
        dept_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if "дата" in col_lower:
                date_col = col
            elif "курьер" in col_lower and "фот" in col_lower:
                fot_couriers_col = col
            elif "повар" in col_lower and "фот" in col_lower:
                fot_cooks_col = col
            elif "уборщиц" in col_lower and "фот" in col_lower:
                fot_cleaners_col = col
            elif "торгов" in col_lower or "предприят" in col_lower or "филиал" in col_lower:
                dept_col = col
        
        if not date_col:
            continue
        
        report_date = row[date_col]
        if pd.isna(report_date):
            continue
        
        # Преобразуем дату
        if isinstance(report_date, str):
            try:
                report_date = datetime.strptime(report_date, "%d.%m.%Y").date()
            except:
                continue
        
        department = normalize_department_name(row.get(dept_col, ""))
        fot_couriers = float(row.get(fot_couriers_col, 0) or 0)
        fot_cooks = float(row.get(fot_cooks_col, 0) or 0)
        fot_cleaners = float(row.get(fot_cleaners_col, 0) or 0)
        
        rows.append({
            "report_date": report_date,
            "department": department,
            "fot_couriers": fot_couriers,
            "fot_cooks": fot_cooks,
            "fot_cleaners": fot_cleaners,
            "raw_data": row.to_dict()
        })
    
    if not rows:
        print("⚠️  Нет валидных данных для загрузки")
        return
    
    # Загружаем в БД
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        execute_values(
            cur,
            """
            INSERT INTO sheets_raw_fot 
            (report_date, department, fot_couriers, fot_cooks, fot_cleaners, raw_data)
            VALUES %s
            ON CONFLICT (report_date, department) 
            DO UPDATE SET
                fot_couriers = EXCLUDED.fot_couriers,
                fot_cooks = EXCLUDED.fot_cooks,
                fot_cleaners = EXCLUDED.fot_cleaners,
                raw_data = EXCLUDED.raw_data,
                loaded_at = CURRENT_TIMESTAMP
            """,
            [
                (
                    row["report_date"],
                    row["department"],
                    row["fot_couriers"],
                    row["fot_cooks"],
                    row["fot_cleaners"],
                    json.dumps(row["raw_data"])
                )
                for row in rows
            ]
        )
        print(f"✅ Загружено {len(rows)} строк")
    finally:
        cur.close()
        conn.close()


def run_sheets_etl(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    """
    Запустить полный ETL процесс для данных из Google Sheets.
    
    Args:
        date_from: Дата начала периода (по умолчанию - вчера)
        date_to: Дата окончания периода (по умолчанию - вчера)
    """
    if date_from is None:
        date_from = datetime.now() - timedelta(days=1)
    if date_to is None:
        date_to = datetime.now() - timedelta(days=1)
    
    try:
        load_direct_data(date_from, date_to)
        load_fot_data(date_from, date_to)
        
        print("✅ ETL процесс для Google Sheets завершен успешно")
    except Exception as e:
        print(f"❌ Ошибка при выполнении ETL: {e}")
        raise


if __name__ == "__main__":
    import json
    import pandas as pd
    
    # Запуск ETL для вчерашнего дня
    run_sheets_etl()
