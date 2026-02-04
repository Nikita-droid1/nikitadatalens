# Как создать GitHub Actions workflow вручную

Если workflow не отображается автоматически, создай его вручную через веб-интерфейс GitHub.

## Способ 1: Через веб-интерфейс GitHub (рекомендуется)

1. **Открой свой репозиторий на GitHub**

2. **Создай папку `.github/workflows/`:**
   - Нажми кнопку **"Add file"** → **"Create new file"**
   - В поле имени файла введи: `.github/workflows/etl.yml`
   - GitHub автоматически создаст папку `.github` и подпапку `workflows`

3. **Скопируй содержимое workflow файла** (см. ниже)

4. **Вставь в редактор** и нажми **"Commit new file"**

---

## Способ 2: Через терминал (если есть доступ)

```bash
cd /путь/к/твоему/репозиторию
mkdir -p .github/workflows
# Скопируй файл daily_etl.yml в .github/workflows/
git add .github/workflows/daily_etl.yml
git commit -m "Add GitHub Actions workflow"
git push
```

---

## Содержимое файла `.github/workflows/etl.yml`

Скопируй это содержимое в файл:

```yaml
name: ETL (ручной запуск)

on:
  workflow_dispatch:  # Только ручной запуск через кнопку

jobs:
  etl:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run ETL process
        env:
          IIKO_BASE_URL: ${{ secrets.IIKO_BASE_URL }}
          IIKO_LOGIN: ${{ secrets.IIKO_LOGIN }}
          IIKO_PASSWORD_SHA1: ${{ secrets.IIKO_PASSWORD_SHA1 }}
          NEON_DATABASE_URL: ${{ secrets.NEON_DATABASE_URL }}
          GOOGLE_SHEETS_CREDENTIALS: ${{ secrets.GOOGLE_SHEETS_CREDENTIALS }}
        run: |
          python etl.py
      
      - name: Run transforms
        env:
          NEON_DATABASE_URL: ${{ secrets.NEON_DATABASE_URL }}
        run: |
          python neon/transforms/run_transforms.py
      
      - name: Notify on failure
        if: failure()
        run: |
          echo "ETL процесс завершился с ошибкой"
```

---

## Проверка

После создания файла:

1. Перейди во вкладку **Actions** в репозитории
2. Должен появиться workflow **"ETL (ручной запуск)"**
3. Нажми на него → **"Run workflow"** → **"Run workflow"**

Если workflow появился — всё готово! Можно переходить к добавлению секретов.
