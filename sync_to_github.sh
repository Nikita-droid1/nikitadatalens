#!/bin/bash
# Скрипт для синхронизации папки проекта с папкой для GitHub

SOURCE_DIR="/Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика"
TARGET_DIR="/Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика_github"

echo "🔄 Синхронизация с папкой для GitHub..."

# Создаем целевую папку если её нет
mkdir -p "$TARGET_DIR"

# Копируем файлы, исключая секреты и локальные файлы
rsync -av \
  --exclude='.env' \
  --exclude='.env.local' \
  --exclude='*.env' \
  --exclude='.git' \
  --exclude='.DS_Store' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.venv' \
  --exclude='venv' \
  --exclude='.Python' \
  --exclude='iiko/api/out/' \
  --exclude='*.json' \
  --include='**/docs/**/*.json' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

echo "✅ Синхронизация завершена!"
echo ""
echo "📋 Проверка:"
if [ -f "$TARGET_DIR/.env" ]; then
  echo "❌ ВНИМАНИЕ: .env попал в папку для GitHub!"
else
  echo "✅ .env отсутствует (правильно)"
fi

if [ -f "$TARGET_DIR/.github/workflows/daily_etl.yml" ]; then
  echo "✅ Workflow файл на месте"
else
  echo "❌ Workflow файл отсутствует!"
fi

echo ""
echo "📝 Следующий шаг:"
echo "   cd $TARGET_DIR"
echo "   git add ."
echo "   git commit -m 'Обновление проекта'"
echo "   git push"
