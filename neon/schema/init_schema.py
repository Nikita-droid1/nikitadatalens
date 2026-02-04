"""
Скрипт для инициализации схемы БД в Neon.
Выполняет все SQL файлы в правильном порядке.
"""
import os
import psycopg2
from dotenv import load_dotenv


def init_schema():
    """Инициализировать схему БД, выполнив все SQL файлы."""
    load_dotenv()
    
    if not os.environ.get("NEON_DATABASE_URL"):
        raise ValueError("NEON_DATABASE_URL не установлена")
    
    # Порядок выполнения SQL файлов
    sql_files = [
        "001_iiko_raw.sql",
        "002_sheets_raw.sql",
        "003_mart.sql"
    ]
    
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    cur = conn.cursor()
    
    try:
        schema_dir = os.path.dirname(__file__)
        
        for sql_file in sql_files:
            sql_path = os.path.join(schema_dir, sql_file)
            
            print(f"📄 Выполнение {sql_file}...")
            
            with open(sql_path, "r", encoding="utf-8") as f:
                sql = f.read()
            
            # Выполняем SQL (может содержать несколько запросов)
            cur.execute(sql)
            conn.commit()
            
            print(f"✅ {sql_file} выполнен успешно")
        
        print("\n✅ Схема БД инициализирована успешно")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при инициализации схемы: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    init_schema()
