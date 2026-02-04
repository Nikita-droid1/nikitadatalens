#!/usr/bin/env python3
"""
Скрипт для синхронизации основной папки проекта с папкой для GitHub.
Исключает секреты и локальные файлы.
"""
import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("/Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика")
TARGET_DIR = Path("/Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика_github")

# Что исключать из копирования
EXCLUDES = {
    '.env', '.env.local', '*.env',
    '.git', '.DS_Store',
    '__pycache__', '*.pyc', '.venv', 'venv', '.Python',
    'iiko/api/out/',
    '.github_changes_tracker.md',  # Временный файл отслеживания
    'ИНСТРУКЦИЯ_ОТСЛЕЖИВАНИЯ.md'  # Локальная инструкция
}

# Паттерны для исключения
EXCLUDE_PATTERNS = ['*.json']  # кроме docs/**/*.json


def should_exclude(path: Path) -> bool:
    """Проверяет, нужно ли исключить файл/папку."""
    path_str = str(path)
    
    # Всегда включаем .github (нужен для workflow) и .gitignore
    if '.github' in path_str or path.name == '.gitignore':
        return False
    
    # Проверяем имя файла/папки
    if path.name in EXCLUDES:
        return True
    
    # Проверяем имя файла/папки
    if path.name in EXCLUDES:
        return True
    
    # Проверяем расширения
    if any(path.name.endswith(ext.replace('*', '')) for ext in EXCLUDE_PATTERNS if '*' in ext):
        # Исключаем JSON, кроме тех что в docs
        if 'docs' not in path_str:
            return True
    
    # Проверяем пути
    for exclude in EXCLUDES:
        if exclude in path_str:
            return True
    
    return False


def sync_directories():
    """Синхронизирует директории."""
    print("🔄 Синхронизация с папкой для GitHub...")
    
    # Создаем целевую папку
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    copied_files = 0
    skipped_files = 0
    
    # Копируем файлы
    for root, dirs, files in os.walk(SOURCE_DIR):
        # Фильтруем директории
        dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]
        
        for file in files:
            source_path = Path(root) / file
            
            # Пропускаем исключенные файлы
            if should_exclude(source_path):
                skipped_files += 1
                continue
            
            # Вычисляем относительный путь
            rel_path = source_path.relative_to(SOURCE_DIR)
            target_path = TARGET_DIR / rel_path
            
            # Создаем директорию если нужно
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Копируем файл
            try:
                shutil.copy2(source_path, target_path)
                copied_files += 1
            except Exception as e:
                print(f"⚠️  Ошибка при копировании {rel_path}: {e}")
    
    print(f"✅ Скопировано файлов: {copied_files}")
    print(f"⏭️  Пропущено файлов: {skipped_files}")
    
    # Проверки
    print("\n📋 Проверка:")
    if (TARGET_DIR / '.env').exists():
        print("❌ ВНИМАНИЕ: .env попал в папку для GitHub!")
    else:
        print("✅ .env отсутствует (правильно)")
    
    if (TARGET_DIR / '.github' / 'workflows' / 'daily_etl.yml').exists():
        print("✅ Workflow файл на месте")
    else:
        print("❌ Workflow файл отсутствует!")
    
    print(f"\n📁 Папка для GitHub: {TARGET_DIR}")
    print("📝 Следующий шаг: перейди в папку и сделай git add/commit/push")


if __name__ == "__main__":
    sync_directories()
