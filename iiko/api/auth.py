"""
Авторизация в iiko Server API.
"""
import os
import requests


def get_token() -> str:
    """
    Получить токен авторизации для iiko Server API.
    
    Returns:
        str: Токен сессии для дальнейших запросов к API
        
    Raises:
        requests.RequestException: При ошибке запроса к API
    """
    base = os.environ["IIKO_BASE_URL"].rstrip("/")
    login = os.environ["IIKO_LOGIN"]
    password = os.environ["IIKO_PASSWORD_SHA1"]  # SHA1-хеш
    
    url = f"{base}/resto/api/auth"
    params = {"login": login, "pass": password}
    
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    
    token = resp.text.strip()
    print(f"🔑 Token: {token[:6]}...")
    return token
