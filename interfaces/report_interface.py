from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from models.order import Order


class ReportGenerator(ABC):
    @abstractmethod
    def generate_report(self, data: Any) -> str:
        pass


class SalesReportGenerator(ReportGenerator):
    def generate_report(self, orders: List[Order]) -> str:
        if not orders:
            return "Нет данных для отчета по продажам"

        total_revenue = sum(order.get_total_price() for order in orders)
        avg_order_value = total_revenue / len(orders)

        result = "=== ОТЧЕТ ПО ПРОДАЖАМ ===\n"
        result += f"Период: {orders[0].creation_time.strftime('%Y-%m-%d')} - "
        result += f"{orders[-1].creation_time.strftime('%Y-%m-%d')}\n"
        result += f"Количество заказов: {len(orders)}\n"
        result += f"Общая выручка: {total_revenue:.2f} лей.\n"
        result += f"Средний чек: {avg_order_value:.2f} лей.\n"

        # Популярные блюда
        dish_counts = {}
        for order in orders:
            for item in order.items:
                dish_name = item.menu_item.name
                if dish_name in dish_counts:
                    dish_counts[dish_name] += item.quantity
                else:
                    dish_counts[dish_name] = item.quantity

        result += "\nПопулярные блюда:\n"
        for dish, count in sorted(dish_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            result += f"  {dish}: {count} шт.\n"

        return result


class InventoryReportGenerator(ReportGenerator):
    def generate_report(self, inventory_data: Dict[str, Dict]) -> str:
        if not inventory_data:
            return "Нет данных для отчета по инвентарю"

        result = "=== ОТЧЕТ ПО ИНВЕНТАРЮ ===\n"
        result += f"Дата: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for category, items in inventory_data.items():
            result += f"{category}:\n"
            for item_name, item_data in items.items():
                result += f"  {item_name}: {item_data['quantity']} {item_data['unit']} "
                result += f"(мин. запас: {item_data['min_quantity']})\n"

                if item_data['quantity'] < item_data['min_quantity']:
                    result += f"    !!! ТРЕБУЕТСЯ ПОПОЛНЕНИЕ !!!\n"

            result += "\n"

        return result


class FinancialReportGenerator(ReportGenerator):
    def generate_report(self, data: Dict) -> str:
        revenue = data.get("revenue", 0)
        expenses = data.get("expenses", {})
        period = data.get("period", "")

        result = "=== ФИНАНСОВЫЙ ОТЧЕТ ===\n"
        result += f"Период: {period}\n\n"
        result += f"Выручка: {revenue:.2f} лей.\n\n"

        result += "Расходы:\n"
        total_expenses = 0
        for category, amount in expenses.items():
            result += f"  {category}: {amount:.2f} лей.\n"
            total_expenses += amount

        result += f"\nИтого расходы: {total_expenses:.2f} лей.\n"
        profit = revenue - total_expenses
        result += f"Прибыль: {profit:.2f} лей.\n"

        return result
