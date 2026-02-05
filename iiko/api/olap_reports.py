"""
Получение OLAP отчетов из iiko Server API.
"""
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
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
    
    # Убеждаемся, что date_from - начало дня, date_to - начало следующего дня (IncludeHigh: False)
    # Если запрашиваем 01.01.2026, то To должен быть 02.01.2026 0:00:00
    date_from_start = date_from.replace(hour=0, minute=0, second=0, microsecond=0)
    date_to_start = (date_to + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Формат даты для iiko API: "01.02.2026 0:00:00" (без ведущего нуля в часах)
    # Используем замену для удаления ведущего нуля в часах
    date_from_str = date_from_start.strftime("%d.%m.%Y %H:%M:%S").replace(" 00:", " 0:")
    date_to_str = date_to_start.strftime("%d.%m.%Y %H:%M:%S").replace(" 00:", " 0:")
    
    # Эндпоинт для получения OLAP отчета
    url = f"{base}/resto/api/v2/reports/olap"
    
    # iiko Server API требует POST запрос с JSON телом
    # Согласно ошибке API, reportType должен быть одним из: STOCK, SALES, TRANSACTIONS, DELIVERIES
    # Для отчетов о продажах (Маржа, Нагрузка, Типы скидок) используем SALES
    # Название отчета должно точно совпадать с названием в iiko
    # Фильтры для отчета "Маржа":
    # - SessionID.OperDay: FilterDateRangeCriteria (обязательный)
    # - DeletedWithWriteoff: FilterIncludeValuesCriteria (NOT_DELETED)
    # - Delivery.ServiceType: FilterIncludeValuesCriteria (COURIER, PICKUP)
    # - OrderDeleted: FilterIncludeValuesCriteria (NOT_DELETED)
    filters = {
        "SessionID.OperDay": {
            "filterType": "resto.back.reports.olap.engine.FilterDateRangeCriteria",
            "From": date_from_str,
            "To": date_to_str,
            "IncludeLow": True,
            "IncludeHigh": False
        },
        "DeletedWithWriteoff": {
            "filterType": "resto.back.reports.olap.engine.FilterIncludeValuesCriteria",
            "DishDeletionStatus": "NOT_DELETED"
        },
        "Delivery.ServiceType": {
            "filterType": "resto.back.reports.olap.engine.FilterIncludeValuesCriteria",
            "DeliveryType": ["COURIER", "PICKUP"]
        },
        "OrderDeleted": {
            "filterType": "resto.back.reports.olap.engine.FilterIncludeValuesCriteria",
            "OrderDeletionStatus": "NOT_DELETED"
        }
    }
    
    json_data = {
        "id": report_id,
        "reportType": "SALES",  # Тип отчета: SALES для отчетов о продажах
        "filters": filters
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
