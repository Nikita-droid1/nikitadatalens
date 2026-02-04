# Настройка Google Sheets API

**Назначение:** получение credentials для доступа к Google Sheets API через сервисный аккаунт.

## Шаг 1: Создание проекта в Google Cloud Console

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Войдите в свой Google аккаунт
3. Создайте новый проект (или выберите существующий):
   - Нажмите на выпадающий список проектов вверху
   - Нажмите **"New Project"**
   - Введите название (например, "Room Broom Analytics")
   - Нажмите **"Create"**

## Шаг 2: Включение Google Sheets API

1. В меню слева выберите **"APIs & Services"** → **"Library"**
2. В поиске введите **"Google Sheets API"**
3. Нажмите на **"Google Sheets API"**
4. Нажмите кнопку **"Enable"** (Включить)

## Шаг 3: Создание сервисного аккаунта

1. Перейдите в **"APIs & Services"** → **"Credentials"**
2. Нажмите **"Create Credentials"** → **"Service Account"**
3. Заполните форму:
   - **Service account name:** `room-broom-sheets` (или любое другое имя)
   - **Service account ID:** автоматически заполнится
   - **Description:** `Service account for Room Broom analytics` (опционально)
4. Нажмите **"Create and Continue"**
5. В разделе **"Grant this service account access to project"** можно пропустить (нажать **"Continue"**)
6. В разделе **"Grant users access to this service account"** можно пропустить (нажать **"Done"**)

## Шаг 4: Создание ключа (JSON)

1. В списке сервисных аккаунтов найдите созданный аккаунт
2. Нажмите на email сервисного аккаунта (например, `room-broom-sheets@your-project.iam.gserviceaccount.com`)
3. Перейдите на вкладку **"Keys"**
4. Нажмите **"Add Key"** → **"Create new key"**
5. Выберите формат **JSON**
6. Нажмите **"Create"**
7. JSON файл автоматически скачается на ваш компьютер

**⚠️ ВАЖНО:** Сохраните этот файл в безопасном месте! Он содержит приватный ключ.

## Шаг 5: Предоставление доступа к Google Sheets

1. Откройте вашу Google Таблицу (например, `https://docs.google.com/spreadsheets/d/1jq1dJdORNRbpboSd-miAglnnqyoK8328s1bwx5QuyHU/edit`)
2. Нажмите кнопку **"Share"** (Поделиться) в правом верхнем углу
3. Вставьте **email сервисного аккаунта** (из шага 3, например `room-broom-sheets@your-project.iam.gserviceaccount.com`)
4. Выберите уровень доступа: **"Editor"** (Редактор) или **"Viewer"** (Зритель, если только читаете данные)
5. Снимите галочку **"Notify people"** (чтобы не отправлять уведомление)
6. Нажмите **"Share"**

**Повторите для всех таблиц:**
- Таблица "Директ": `1jq1dJdORNRbpboSd-miAglnnqyoK8328s1bwx5QuyHU`
- Таблица ФОТ: `1JXwkPQtLKUvuf7q9HAqxUcEN52xvMoLc0E7Cr5mQwm8`

## Шаг 6: Получение GOOGLE_SHEETS_CREDENTIALS

1. Откройте скачанный JSON файл в текстовом редакторе
2. Скопируйте **весь** содержимое файла (это один большой JSON объект)
3. Это и есть значение для `GOOGLE_SHEETS_CREDENTIALS`

**Пример структуры JSON:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "room-broom-sheets@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  ...
}
```

## Шаг 7: Добавление в GitHub Secrets

1. Откройте репозиторий на GitHub
2. Перейдите: **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **"New repository secret"**
4. **Name:** `GOOGLE_SHEETS_CREDENTIALS`
5. **Secret:** вставьте весь JSON из файла (как одну строку)
6. Нажмите **"Add secret"**

**⚠️ ВАЖНО:** 
- JSON должен быть в одну строку (без переносов)
- Или можно использовать многострочный формат в GitHub Secrets (поддерживается)

## Альтернатива: Без Google Sheets

Если вы **не используете** Google Sheets (данные только из iiko API), то:
- Просто **не добавляйте** секрет `GOOGLE_SHEETS_CREDENTIALS` в GitHub
- ETL скрипт автоматически пропустит загрузку из Google Sheets
- В логах будет: `⚠️ GOOGLE_SHEETS_CREDENTIALS не установлена, пропускаем загрузку из Google Sheets`

## Проверка

После добавления секрета в GitHub, при запуске workflow вы должны увидеть в логах:
- ✅ Загрузка данных из таблицы "Директ"
- ✅ Загрузка данных ФОТ

Если видите ошибки доступа — проверьте, что сервисный аккаунт добавлен как редактор в таблицы.
