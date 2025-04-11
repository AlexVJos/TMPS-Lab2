from typing import List, Dict
from datetime import datetime
from models.menu_item import MenuItem


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int = 1):
        self.menu_item = menu_item
        self.quantity = quantity

    def get_total_price(self) -> float:
        return self.menu_item.get_price() * self.quantity

    def __str__(self) -> str:
        return f"{self.menu_item.name} x{self.quantity} = {self.get_total_price():.2f} лей."


class Order:
    def __init__(self, order_id: int, table_number: int):
        self.order_id = order_id
        self.table_number = table_number
        self.items: List[OrderItem] = []
        self.creation_time = datetime.now()
        self.status = "Created"
        self.payment_status = "Unpaid"

    def add_item(self, menu_item: MenuItem, quantity: int = 1):
        for item in self.items:
            if item.menu_item.name == menu_item.name:
                item.quantity += quantity
                return

        self.items.append(OrderItem(menu_item, quantity))

    def remove_item(self, item_name: str, quantity: int = 1):
        for i, item in enumerate(self.items):
            if item.menu_item.name == item_name:
                if item.quantity <= quantity:
                    self.items.pop(i)
                else:
                    item.quantity -= quantity
                return True
        return False

    def get_total_price(self) -> float:
        return sum(item.get_total_price() for item in self.items)

    def change_status(self, status: str):
        self.status = status

    def mark_as_paid(self, payment_method: str):
        self.payment_status = f"Paid ({payment_method})"

    def __str__(self) -> str:
        result = f"Заказ #{self.order_id} (Стол {self.table_number})\n"
        result += f"Статус: {self.status}, Оплата: {self.payment_status}\n"
        result += "Элементы заказа:\n"

        for item in self.items:
            result += f"  {item}\n"

        result += f"Итого: {self.get_total_price():.2f} лей."
        return result


class OrderManager:
    def __init__(self):
        self.orders: Dict[int, Order] = {}
        self.next_order_id = 1

    def create_order(self, table_number: int) -> Order:
        order = Order(self.next_order_id, table_number)
        self.orders[self.next_order_id] = order
        self.next_order_id += 1
        return order

    def get_order(self, order_id: int) -> Order:
        return self.orders.get(order_id)

    def get_all_orders(self) -> List[Order]:
        return list(self.orders.values())

    def get_active_orders(self) -> List[Order]:
        return [order for order in self.orders.values() if order.status != "Completed"]

    def get_table_orders(self, table_number: int) -> List[Order]:
        return [order for order in self.orders.values() if order.table_number == table_number]
