"""
Главный ETL скрипт для запуска всех процессов выгрузки данных.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

from iiko.api.extract import run_iiko_etl
from google_sheets.load import run_sheets_etl


def main(date_from: Optional[datetime] = None, date_to: Optional[datetime] = None):
    """
    Запустить полный ETL процесс.
    
    Args:
        date_from: Дата начала периода (по умолчанию - вчера)
        date_to: Дата окончания периода (по умолчанию - вчера)
    """
    # Загружаем переменные окружения из .env
    load_dotenv()
    
    if date_from is None:
        date_from = datetime.now() - timedelta(days=1)
    if date_to is None:
        date_to = datetime.now() - timedelta(days=1)
    
    print(f"🚀 Запуск ETL процесса за период {date_from.date()} - {date_to.date()}")
    print("=" * 60)
    
    # Проверяем наличие необходимых переменных окружения
    required_vars = [
        "IIKO_BASE_URL",
        "IIKO_LOGIN",
        "IIKO_PASSWORD_SHA1",
        "NEON_DATABASE_URL"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        raise ValueError(f"Отсутствуют переменные окружения: {', '.join(missing_vars)}")
    
    try:
        # Загружаем данные из iiko API
        print("\n📊 Этап 1: Загрузка данных из iiko Server API")
        print("-" * 60)
        run_iiko_etl(date_from, date_to)
        
        # Загружаем данные из Google Sheets
        print("\n📊 Этап 2: Загрузка данных из Google Sheets")
        print("-" * 60)
        if os.environ.get("GOOGLE_SHEETS_CREDENTIALS"):
            run_sheets_etl(date_from, date_to)
        else:
            print("⚠️  GOOGLE_SHEETS_CREDENTIALS не установлена, пропускаем загрузку из Google Sheets")
        
        print("\n" + "=" * 60)
        print("✅ ETL процесс завершен успешно")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении ETL: {e}")
        raise


if __name__ == "__main__":
    main()
