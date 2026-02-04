"""
Извлечение данных из Google Sheets.
"""
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
from .auth import get_sheets_client, get_sheet_by_url


# URL таблиц
DIRECT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1jq1dJdORNRbpboSd-miAglnnqyoK8328s1bwx5QuyHU/edit?gid=217008063#gid=217008063"
DIRECT_SHEET_NAME = "Директ"

FOT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1JXwkPQtLKUvuf7q9HAqxUcEN52xvMoLc0E7Cr5mQwm8/edit?gid=909952063#gid=909952063"


def extract_direct_data() -> pd.DataFrame:
    """
    Извлечь данные из таблицы "Директ" (рекламный бюджет + ФОТ директ).
    
    Returns:
        pd.DataFrame: DataFrame с колонками: Дата, Рекламный бюджет, ФОТ, Торговое предприятие
    """
    client = get_sheets_client()
    worksheet = get_sheet_by_url(client, DIRECT_SHEET_URL, DIRECT_SHEET_NAME)
    
    # Получаем все данные
    data = worksheet.get_all_records()
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(data)
    
    # Нормализуем названия колонок (убираем пробелы, приводим к нижнему регистру)
    df.columns = df.columns.str.strip().str.lower()
    
    # Преобразуем дату
    if "дата" in df.columns:
        df["дата"] = pd.to_datetime(df["дата"], format="%d.%m.%Y", errors="coerce")
    
    return df


def extract_fot_data() -> pd.DataFrame:
    """
    Извлечь данные из таблицы ФОТ (курьеры, повара, уборщицы).
    
    Returns:
        pd.DataFrame: DataFrame с данными по ФОТ
    """
    client = get_sheets_client()
    worksheet = get_sheet_by_url(client, FOT_SHEET_URL)
    
    # Получаем все данные
    data = worksheet.get_all_records()
    
    # Преобразуем в DataFrame
    df = pd.DataFrame(data)
    
    # Нормализуем названия колонок
    df.columns = df.columns.str.strip().str.lower()
    
    # Преобразуем дату, если есть
    date_columns = [col for col in df.columns if "дата" in col.lower()]
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], format="%d.%m.%Y", errors="coerce")
    
    return df


def get_direct_data_by_date_range(
    date_from: datetime,
    date_to: datetime
) -> pd.DataFrame:
    """
    Получить данные из таблицы "Директ" за указанный период.
    
    Args:
        date_from: Дата начала периода
        date_to: Дата окончания периода
        
    Returns:
        pd.DataFrame: Отфильтрованные данные
    """
    df = extract_direct_data()
    
    if "дата" in df.columns:
        df = df[(df["дата"] >= date_from) & (df["дата"] <= date_to)]
    
    return df


def get_fot_data_by_date_range(
    date_from: datetime,
    date_to: datetime
) -> pd.DataFrame:
    """
    Получить данные ФОТ за указанный период.
    
    Args:
        date_from: Дата начала периода
        date_to: Дата окончания периода
        
    Returns:
        pd.DataFrame: Отфильтрованные данные
    """
    df = extract_fot_data()
    
    # Ищем колонку с датой
    date_columns = [col for col in df.columns if "дата" in col.lower()]
    if date_columns:
        date_col = date_columns[0]
        df = df[(df[date_col] >= date_from) & (df[date_col] <= date_to)]
    
    return df
