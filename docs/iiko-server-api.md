# iiko Server (Resto) API

**Назначение:** документация по iiko Server API (HTTP Resto API), не iikoCloud. Используется для выгрузки данных с вашего сервера iiko (например oreks-co.iiko.it).

## Источники

- **Официальная документация IIKO:** [ru.iiko.help — API](https://ru.iiko.help/articles/#!api-documentations/getting-started)
- **Расширенное описание (PHP SDK):** [iikophpserverapi.readme.io](https://iikophpserverapi.readme.io/docs)
- **Репозиторий PHP SDK:** [aschurf/iikoPhpServerApi](https://github.com/aschurf/iikoPhpServerApi)

## Авторизация

- **Базовый URL сервера** — например `https://oreks-co.iiko.it:443` (переменная `IIKO_BASE_URL`).
- **Логин** — пользователь API (`IIKO_LOGIN`).
- **Пароль** — передаётся как **SHA1-хеш** пароля пользователя (`IIKO_PASSWORD_SHA1`). Само значение пароля в коде не хранить.

**Эндпоинты авторизации** (зависит от версии сервера):

- Вариант 1: `GET {IIKO_BASE_URL}/api/auth?login={IIKO_LOGIN}&pass={IIKO_PASSWORD}` — пароль в открытом виде (`IIKO_PASSWORD`).
- Вариант 2: `GET {IIKO_BASE_URL}/resto/api/auth?login={IIKO_LOGIN}&pass={IIKO_PASSWORD_SHA1}` — пароль как SHA1 (`IIKO_PASSWORD_SHA1`).

При необходимости путь задаётся переменной **IIKO_AUTH_PATH** (по умолчанию `/api/auth`). Ответ — ключ сессии (токен) в теле ответа (текст). В последующих запросах токен передаётся параметром `key=` в query string.

### Как получить SHA1-хеш пароля (для IIKO_PASSWORD_SHA1)

Если сервер ждёт пароль в виде SHA1, посчитать хеш можно так (пароль вводится локально, никуда не отправляется):

**Python (в терминале):**
```bash
python3 -c "import hashlib; print(hashlib.sha1(input('Пароль: ').encode()).hexdigest())"
```
Введи пароль, нажми Enter — в консоль выведется строка из 40 символов (hex). Её и вставляй в секрет IIKO_PASSWORD_SHA1.

**PowerShell:**
```powershell
$password = Read-Host "Пароль" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
$plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($plain)
$sha1 = [System.Security.Cryptography.SHA1]::Create().ComputeHash($bytes)
[BitConverter]::ToString($sha1).Replace("-","").ToLower()
[System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
```

**macOS / Linux (openssl):**
```bash
echo -n "ТВОЙ_ПАРОЛЬ" | openssl dgst -sha1 | awk '{print $2}'
```
Замени `ТВОЙ_ПАРОЛЬ` на пароль или используй `read -s` и pipe, чтобы не светить пароль в истории.

## Лицензия

Подключение к API занимает **1 слот лицензии** iiko. После завершения выгрузки сессию нужно закрывать (освобождать лицензию). В PHP SDK для этого используется метод `close()`.

## Методы API

По README PHP SDK минимально описан метод **getStores()** (список складов организации). Полный перечень методов — в [iikophpserverapi.readme.io](https://iikophpserverapi.readme.io/docs) и [ru.iiko.help](https://ru.iiko.help/articles/#!api-documentations/getting-started). Эндпоинты отчётов/заказов для выгрузки в Neon уточняйте по документации или у администратора сервера.

## Пример запроса авторизации

**PowerShell:**

```powershell
$base = "https://oreks-co.iiko.it:443"
$login = "ЛОГИН"
$sha1 = "ПАРОЛЬ"   # SHA1-хеш пароля
(iwr "$base/resto/api/auth?login=$login&pass=$sha1" -UseBasicParsing).Content
```

**Python (получение токена, как у коллеги — пароль в открытом виде, путь /api/auth):**

```python
import os
import requests

base = os.environ["IIKO_BASE_URL"].rstrip("/")
login = os.environ["IIKO_LOGIN"]
password = os.environ["IIKO_PASSWORD"]  # или IIKO_PASSWORD_SHA1, если сервер ждёт хеш

url = f"{base}/api/auth"
params = {"login": login, "pass": password}
r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
token = r.text.strip()
```

Дальнейшие запросы к API выполняются с параметром `key={token}` в URL или в заголовке (по документации вашей версии API).
