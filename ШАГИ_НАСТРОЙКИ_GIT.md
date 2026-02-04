# Пошаговая настройка Git в терминале Cursor

## Шаг 1: Открой терминал

В Cursor: **Terminal** → **New Terminal** (или `Ctrl + \``)

---

## Шаг 2: Перейди в папку проекта

В терминале выполни:

```bash
cd /Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика
```

**Проверка:** Должна появиться строка с путем к папке.

---

## Шаг 3: Инициализируй Git

```bash
git init
```

**Ожидаемый результат:** `Initialized empty Git repository in /Users/nikitasmirnov/Desktop/cursor/Работа/1_дата-аналитика/.git/`

---

## Шаг 4: Добавь все файлы

```bash
git add .
```

**Проверка:** Ничего не должно вывестись (это нормально).

---

## Шаг 5: Создай первый коммит

```bash
git commit -m "Initial commit: ETL pipeline for Room Broom"
```

**Ожидаемый результат:** Должно быть сообщение о создании коммита с количеством файлов.

---

## Шаг 6: Подключи к GitHub

**Замени `ТВОЙ_ЛОГИН` и `НАЗВАНИЕ_РЕПОЗИТОРИЯ` на реальные значения:**

```bash
git remote add origin https://github.com/ТВОЙ_ЛОГИН/НАЗВАНИЕ_РЕПОЗИТОРИЯ.git
```

**Проверка:**
```bash
git remote -v
```

Должна показаться ссылка на твой репозиторий.

---

## Шаг 7: Отправь код в GitHub

```bash
git push -u origin main
```

**Если спросит логин/пароль:**
- Используй Personal Access Token (не пароль)
- Или настрой SSH ключи

**Ожидаемый результат:** Код должен отправиться на GitHub.

---

## Проверка

После выполнения всех шагов:

1. Открой репозиторий на GitHub
2. Убедись, что все файлы видны
3. Проверь вкладку Actions — должен быть workflow

---

## Если что-то не работает

**Ошибка:** `fatal: not a git repository`
- **Решение:** Выполни `git init` (шаг 3)

**Ошибка:** `remote origin already exists`
- **Решение:** Выполни `git remote remove origin`, затем шаг 6 заново

**Ошибка:** `authentication failed`
- **Решение:** Нужен Personal Access Token вместо пароля (см. ниже)

---

## Как получить Personal Access Token для GitHub

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выбери права: `repo` (полный доступ к репозиториям)
4. Скопируй токен (показывается только один раз!)
5. Используй токен вместо пароля при `git push`

---

## После настройки

Теперь при изменениях:

1. **В терминале:**
   ```bash
   git add .
   git commit -m "Описание изменений"
   git push
   ```

2. **Или через панель Source Control в Cursor:**
   - Открой панель (`Cmd+Shift+G`)
   - Нажми "+" → Commit → Push
