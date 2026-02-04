"""
Запуск SQL трансформаций для обновления витрины данных.
"""
import os
import psycopg2
from dotenv import load_dotenv


def run_transforms():
    """Запустить SQL трансформации для обновления витрины."""
    # Загружаем переменные окружения
    load_dotenv()
    
    if not os.environ.get("NEON_DATABASE_URL"):
        raise ValueError("NEON_DATABASE_URL не установлена")
    
    # Читаем SQL файл
    sql_file = os.path.join(os.path.dirname(__file__), "refresh_mart.sql")
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql = f.read()
    
    # Подключаемся к БД и выполняем SQL
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    cur = conn.cursor()
    
    try:
        print("🔄 Запуск трансформаций для обновления витрины данных...")
        
        # Выполняем SQL (может содержать несколько запросов)
        cur.execute(sql)
        conn.commit()
        
        print("✅ Трансформации выполнены успешно")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при выполнении трансформаций: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run_transforms()
