# Как загрузить проект в GitHub

## Шаг 1: Создать репозиторий на GitHub

1. Открой [github.com](https://github.com)
2. Нажми **"New repository"** (или **"+"** → **"New repository"**)
3. Заполни:
   - **Repository name:** `room-broom-analytics` (или любое другое имя)
   - **Description:** `ETL pipeline for Room Broom analytics`
   - **Public** или **Private** (на твое усмотрение)
   - **НЕ** ставь галочки на "Initialize with README" и других опциях
4. Нажми **"Create repository"**

## Шаг 2: Загрузить код в репозиторий

### Вариант А: Через терминал (если уже есть Git)

Открой терминал и выполни:

```bash
cd /Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика

# Проверь, что .env не попадет в репозиторий
git status

# Добавь все файлы (кроме .env - он в .gitignore)
git add .

# Создай коммит
git commit -m "Initial commit: ETL pipeline for Room Broom"

# Подключи удаленный репозиторий (замени на свою ссылку)
git remote add origin https://github.com/ТВОЙ_ЛОГИН/room-broom-analytics.git

# Отправь код на GitHub
git push -u origin main
```

**Важно:** Замени `ТВОЙ_ЛОГИН` и `room-broom-analytics` на реальные значения из твоего репозитория.

### Вариант Б: Через GitHub Desktop (проще)

1. Скачай [GitHub Desktop](https://desktop.github.com/)
2. Установи и войди в свой GitHub аккаунт
3. **File** → **Add Local Repository**
4. Выбери папку: `/Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика`
5. Внизу слева напиши: "Initial commit: ETL pipeline"
6. Нажми **"Commit to main"**
7. Нажми **"Publish repository"** (или **"Push origin"** если репозиторий уже создан)

## Шаг 3: Проверка

1. Открой свой репозиторий на GitHub
2. Убедись, что все файлы видны:
   - ✅ Должна быть папка `.github/workflows/`
   - ✅ Должен быть файл `etl.py`
   - ✅ Должны быть все Python модули
   - ✅ Должны быть SQL файлы
   - ❌ Файла `.env` НЕ должно быть (он в `.gitignore`)

3. Перейди во вкладку **Actions**
4. Должен появиться workflow **"ETL (ручной запуск)"**

## Готово!

Теперь можно:
- Добавлять секреты в GitHub (ШАГ 1 из чеклиста)
- Запускать ETL вручную через кнопку "Run workflow"

---

## Если что-то пошло не так

### Файл .env попал в репозиторий?

Удали его:
```bash
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

### Не могу подключить репозиторий?

Проверь ссылку на репозиторий. Она должна быть вида:
`https://github.com/ТВОЙ_ЛОГИН/НАЗВАНИЕ_РЕПО.git`

### Git не установлен?

Установи с [git-scm.com](https://git-scm.com/) или используй GitHub Desktop.
