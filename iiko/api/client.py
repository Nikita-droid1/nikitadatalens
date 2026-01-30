"""
Клиент iiko Server (Resto) API.
Авторизация: GET /api/auth?login=&pass= (пароль в открытом виде или SHA1 — см. IIKO_PASSWORD / IIKO_PASSWORD_SHA1).
Секреты: IIKO_BASE_URL, IIKO_LOGIN, IIKO_PASSWORD или IIKO_PASSWORD_SHA1. См. docs/iiko-server-api.md.
"""

import os
import requests


def get_env(name: str, default: str = "") -> str:
    v = os.environ.get(name, default).strip()
    if not v:
        raise ValueError(f"Не задана переменная окружения: {name}")
    return v


class IikoClient:
    def __init__(self, base_url: str = "", api_login: str = "", password: str = ""):
        self.base_url = (base_url or os.environ.get("IIKO_BASE_URL") or os.environ.get("IIKO_API_URL", "")).rstrip("/")
        if not self.base_url:
            raise ValueError("Не задана переменная окружения: IIKO_BASE_URL или IIKO_API_URL")
        self.api_login = api_login or os.environ.get("IIKO_LOGIN") or os.environ.get("IIKO_API_LOGIN")
        if not self.api_login:
            raise ValueError("Не задана переменная окружения: IIKO_LOGIN или IIKO_API_LOGIN")
        self._password = password or os.environ.get("IIKO_PASSWORD") or os.environ.get("IIKO_PASSWORD_SHA1", "")
        if not self._password:
            raise ValueError("Не задана переменная окружения: IIKO_PASSWORD или IIKO_PASSWORD_SHA1")
        self._token: str | None = None
        self._auth_path = os.environ.get("IIKO_AUTH_PATH", "/api/auth").strip() or "/api/auth"

    def get_access_token(self) -> str:
        """Получить токен для iiko Server API: GET /api/auth?login=&pass= (ответ — текст токена)."""
        if self._token:
            return self._token
        url = f"{self.base_url}{self._auth_path}"
        params = {"login": self.api_login, "pass": self._password}
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        self._token = resp.text.strip()
        if not self._token:
            raise RuntimeError("В ответе API пустой токен")
        return self._token

    def _request(self, method: str, path: str, json_body: dict | None = None, params: dict | None = None) -> dict:
        token = self.get_access_token()
        url = f"{self.base_url}{path}"
        q = dict(params) if params else {}
        q["key"] = token
        headers = {"Content-Type": "application/json"}
        if json_body is not None:
            r = requests.request(method, url, params=q, json=json_body, headers=headers, timeout=60)
        else:
            r = requests.request(method, url, params=q, headers=headers, timeout=60)
        r.raise_for_status()
        return r.json() if r.content else {}

    def get_organizations(self) -> list:
        """Список организаций (точек). Эндпоинт зависит от версии Resto API."""
        data = self._request("POST", "/api/1/organizations", json_body={})
        return data.get("organizations", [])

    def get_orders_by_delivery_date(
        self,
        delivery_date_from: str,
        delivery_date_to: str | None = None,
        organization_ids: list[str] | None = None,
    ) -> dict:
        """Заказы по дате доставки. Эндпоинт и формат — по документации вашего Resto API."""
        orgs = organization_ids or [o["id"] for o in self.get_organizations()]
        body: dict = {
            "organizationIds": orgs,
            "deliveryDateFrom": delivery_date_from,
        }
        if delivery_date_to:
            body["deliveryDateTo"] = delivery_date_to
        return self._request("POST", "/api/1/deliveries/by_delivery_date_and_status", json_body=body)
