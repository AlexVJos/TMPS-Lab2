from typing import List, Dict
from datetime import datetime, timedelta
from models.order import OrderManager
from interfaces.report_interface import (
    ReportGenerator,
    SalesReportGenerator,
    InventoryReportGenerator,
    FinancialReportGenerator
)


class ReportService:
    def __init__(self, order_manager: OrderManager):
        self.order_manager = order_manager
        self.generators = {
            "sales": SalesReportGenerator(),
            "inventory": InventoryReportGenerator(),
            "financial": FinancialReportGenerator()
        }

    def generate_sales_report(self, start_date: datetime = None, end_date: datetime = None) -> str:
        all_orders = self.order_manager.get_all_orders()

        if start_date is None:
            start_date = datetime.now() - timedelta(days=30)

        if end_date is None:
            end_date = datetime.now()

        filtered_orders = [
            order for order in all_orders
            if start_date <= order.creation_time <= end_date
        ]

        return self.generators["sales"].generate_report(filtered_orders)

    def generate_inventory_report(self, inventory_data: Dict[str, Dict]) -> str:
        return self.generators["inventory"].generate_report(inventory_data)

    def generate_financial_report(self, period: str) -> str:
        all_orders = self.order_manager.get_all_orders()
        revenue = sum(order.get_total_price() for order in all_orders)

        data = {
            "revenue": revenue,
            "expenses": {
                "Продукты": revenue * 0.4,
                "Зарплата": revenue * 0.3,
                "Аренда": revenue * 0.1,
                "Коммунальные услуги": revenue * 0.05,
                "Прочее": revenue * 0.05
            },
            "period": period
        }

        return self.generators["financial"].generate_report(data)

    def add_custom_report_generator(self, name: str, generator: ReportGenerator):
        self.generators[name] = generator

    def get_available_report_types(self) -> List[str]:
        return list(self.generators.keys())
