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
    report_name: Optional[str] = None,
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
    
    # Убеждаемся, что date_from - начало дня, date_to - конец дня
    date_from_start = date_from.replace(hour=0, minute=0, second=0, microsecond=0)
    date_to_end = date_to.replace(hour=23, minute=59, second=59, microsecond=0)
    
    # Формат даты для iiko API: "01.01.2026 0:00:00" и "01.01.2026 23:59:59"
    date_from_str = date_from_start.strftime("%d.%m.%Y %H:%M:%S")
    date_to_str = date_to_end.strftime("%d.%m.%Y %H:%M:%S")
    
    # Эндпоинт для получения OLAP отчета
    url = f"{base}/resto/api/v2/reports/olap"
    
    # iiko Server API требует POST запрос с JSON телом
    # Согласно ошибке API, reportType должен быть одним из: STOCK, SALES, TRANSACTIONS, DELIVERIES
    # Для отчетов о продажах (Маржа, Нагрузка, Типы скидок) используем SALES
    # Название отчета должно точно совпадать с названием в iiko
    # Обязательно требуется фильтр "Учетный день (OpenDate.Typed)" в поле filters
    # filters должен быть объектом (LinkedHashMap), не массивом
    # Для Jackson полиморфной десериализации нужен @class в каждом фильтре
    # Даты передаются как query параметры И в filters
    json_data = {
        "id": report_id,
        "reportType": "SALES",  # Тип отчета: SALES для отчетов о продажах
        "filters": {
            "OpenDate.Typed": {
                "@class": "resto.back.reports.olap.engine.DateFilterCriteria",
                "filterType": "OpenDate.Typed",
                "from": date_from_str,
                "to": date_to_str
            }
        }
    }
    
    # Добавляем название отчета, если оно указано
    if report_name:
        json_data["name"] = report_name
    
    # Токен и даты передаются как query параметры
    params = {
        "key": token,
        "dateFrom": date_from_str,
        "dateTo": date_to_str
    }
    
    # Выполняем POST запрос
    resp = requests.post(url, json=json_data, params=params, timeout=60)
    
    # Если получили ошибку, выводим детали для диагностики
    if resp.status_code != 200:
        error_detail = resp.text[:500] if resp.text else "Нет деталей ошибки"
        raise requests.HTTPError(
            f"{resp.status_code} {resp.reason} для url: {resp.url}\n"
            f"Детали: {error_detail}\n"
            f"Параметры запроса: id={report_id}, dateFrom={date_from_str}, dateTo={date_to_str}"
        )
    
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
        report_name="Маржа (выручка, % скидки, % себестоимости)",
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
        report_name="Нагрузка по часам (заказы)",
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
        report_name="нагрузка по часам (выручка)",
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
        report_name="Типы скидок (data lens)",
        token=token
    )
