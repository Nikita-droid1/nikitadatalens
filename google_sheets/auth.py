"""
Настройка доступа к Google Sheets API.
"""
import os
import json
from typing import Optional
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import gspread


def get_sheets_client(credentials_json: Optional[str] = None) -> gspread.Client:
    """
    Получить клиент для работы с Google Sheets API.
    
    Args:
        credentials_json: JSON строка с credentials сервисного аккаунта.
                         Если None, берется из переменной окружения GOOGLE_SHEETS_CREDENTIALS.
                         
    Returns:
        gspread.Client: Клиент для работы с Google Sheets
        
    Raises:
        ValueError: Если credentials не найдены
    """
    if credentials_json is None:
        credentials_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    
    if not credentials_json:
        raise ValueError(
            "GOOGLE_SHEETS_CREDENTIALS не установлена. "
            "Установите переменную окружения с JSON credentials сервисного аккаунта Google."
        )
    
    # Парсим JSON credentials
    creds_dict = json.loads(credentials_json)
    
    # Создаем credentials объект
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
    )
    
    # Создаем клиент gspread
    client = gspread.authorize(credentials)
    
    return client


def get_sheet_by_url(client: gspread.Client, url: str, sheet_name: Optional[str] = None):
    """
    Получить лист из Google Sheets по URL.
    
    Args:
        client: Клиент gspread
        url: URL Google Sheets (полный или только ID)
        sheet_name: Название вкладки (если None, берется первая вкладка)
        
    Returns:
        gspread.Worksheet: Объект листа
    """
    # Извлекаем ID из URL
    if "/spreadsheets/d/" in url:
        sheet_id = url.split("/spreadsheets/d/")[1].split("/")[0]
    elif "/d/" in url:
        sheet_id = url.split("/d/")[1].split("/")[0]
    else:
        sheet_id = url  # Предполагаем, что это уже ID
    
    # Открываем таблицу
    spreadsheet = client.open_by_key(sheet_id)
    
    # Получаем нужный лист
    if sheet_name:
        worksheet = spreadsheet.worksheet(sheet_name)
    else:
        worksheet = spreadsheet.sheet1  # Первая вкладка
    
    return worksheet
