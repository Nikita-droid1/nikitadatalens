"""
Получение OLAP отчетов из iiko Server API.
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from .auth import get_token


def get_olap_report(
    report_id: str,
    date_from: datetime,
    date_to: datetime,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получить OLAP отчет по ID из iiko Server API.
    
    Args:
        report_id: ID отчета (например, '906ba511-1717-485c-aa60-2b47d03c49ec')
        date_from: Дата начала периода
        date_to: Дата окончания периода
        token: Токен авторизации (если None, будет получен автоматически)
        
    Returns:
        dict: Данные отчета в формате JSON
        
    Raises:
        requests.RequestException: При ошибке запроса к API
    """
    if token is None:
        token = get_token()
    
    base = os.environ["IIKO_BASE_URL"].rstrip("/")
    
    # Формат даты для iiko API: "01.01.2026 0:00:00"
    date_from_str = date_from.strftime("%d.%m.%Y %H:%M:%S")
    date_to_str = date_to.strftime("%d.%m.%Y %H:%M:%S")
    
    # Эндпоинт для получения OLAP отчета
    # Точный формат может отличаться, нужно уточнить по документации
    url = f"{base}/resto/api/v2/reports/olap"
    
    # Параметры запроса
    params = {
        "key": token,
        "reportId": report_id,
        "dateFrom": date_from_str,
        "dateTo": date_to_str
    }
    
    # Альтернативный вариант через POST с телом запроса
    # Попробуем сначала GET, если не сработает - перейдем на POST
    try:
        resp = requests.get(url, params=params, timeout=60)
        if resp.status_code == 405:  # Method Not Allowed - значит нужен POST
            resp = requests.post(url, json={
                "reportId": report_id,
                "dateFrom": date_from_str,
                "dateTo": date_to_str
            }, params={"key": token}, timeout=60)
    except requests.RequestException:
        # Пробуем POST вариант
        resp = requests.post(url, json={
            "reportId": report_id,
            "dateFrom": date_from_str,
            "dateTo": date_to_str
        }, params={"key": token}, timeout=60)
    
    resp.raise_for_status()
    return resp.json()


def get_margin_report(
    date_from: datetime,
    date_to: datetime,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получить отчет "Маржа" (выручка, % скидки, % себестоимости).
    
    ID отчета: 906ba511-1717-485c-aa60-2b47d03c49ec
    """
    return get_olap_report(
        report_id="906ba511-1717-485c-aa60-2b47d03c49ec",
        date_from=date_from,
        date_to=date_to,
        token=token
    )


def get_load_orders_report(
    date_from: datetime,
    date_to: datetime,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получить отчет "Нагрузка по часам (заказы)".
    
    ID отчета: cd0c03aa-6ac8-433a-8d60-823d515ab968
    """
    return get_olap_report(
        report_id="cd0c03aa-6ac8-433a-8d60-823d515ab968",
        date_from=date_from,
        date_to=date_to,
        token=token
    )


def get_load_revenue_report(
    date_from: datetime,
    date_to: datetime,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получить отчет "Нагрузка по часам (выручка)".
    
    ID отчета: 6c37631c-5cc5-4644-b25e-3411a3492e37
    """
    return get_olap_report(
        report_id="6c37631c-5cc5-4644-b25e-3411a3492e37",
        date_from=date_from,
        date_to=date_to,
        token=token
    )


def get_discount_types_report(
    date_from: datetime,
    date_to: datetime,
    token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Получить отчет "Типы скидок (data lens)".
    
    ID отчета: 8ac9c323-034e-4b21-9eb6-60de5e05fbea
    """
    return get_olap_report(
        report_id="8ac9c323-034e-4b21-9eb6-60de5e05fbea",
        date_from=date_from,
        date_to=date_to,
        token=token
    )
