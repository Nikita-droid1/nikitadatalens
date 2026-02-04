"""
Модуль для работы с iiko Server API.
"""
from .auth import get_token
from .olap_reports import (
    get_olap_report,
    get_margin_report,
    get_load_orders_report,
    get_load_revenue_report,
    get_discount_types_report
)

__all__ = [
    "get_token",
    "get_olap_report",
    "get_margin_report",
    "get_load_orders_report",
    "get_load_revenue_report",
    "get_discount_types_report",
]
