from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from models.menu_item import MenuItem, MenuCategory
from models.order import Order, OrderManager
from services.payment_service import PaymentService
from services.notification_service import StaffNotificationService
from services.report_service import ReportService
from adapters.legacy_system_adapter import (
    LegacyInventorySystem,
    InventoryAdapter,
    LegacyEmployeeSystem,
    StaffAdapter
)


class RestaurantFacade:
    def __init__(self):
        self.order_manager = OrderManager()

        legacy_inventory = LegacyInventorySystem()
        self.inventory_adapter = InventoryAdapter(legacy_inventory)

        legacy_staff = LegacyEmployeeSystem()
        self.staff_adapter = StaffAdapter(legacy_staff)

        self.payment_service = PaymentService()
        self.notification_service = StaffNotificationService()
        self.report_service = ReportService(self.order_manager)

        self.menu = self._initialize_menu()

    def _initialize_menu(self) -> MenuCategory:
        menu = MenuCategory("Меню ресторана")

        appetizers = MenuCategory("Закуски", "Легкие блюда для начала трапезы")
        main_courses = MenuCategory("Основные блюда", "Сытные блюда для основной части трапезы")
        desserts = MenuCategory("Десерты", "Сладкие блюда для завершения трапезы")
        drinks = MenuCategory("Напитки", "Освежающие и согревающие напитки")

        appetizers.add(MenuItem("Цезарь с курицей", "Салат с куриным филе, сыром пармезан и соусом цезарь", 350.0))
        appetizers.add(MenuItem("Брускетта с томатами", "Хрустящий багет с томатами и базиликом", 250.0))
        appetizers.add(MenuItem("Карпаччо из говядины", "Тонко нарезанная говядина с рукколой и пармезаном", 450.0))

        main_courses.add(MenuItem("Стейк Рибай", "Стейк из мраморной говядины с гарниром", 1200.0))
        main_courses.add(MenuItem("Паста Карбонара", "Паста с беконом, яйцом и сыром пармезан", 550.0))
        main_courses.add(MenuItem("Филе лосося", "Запеченное филе лосося с овощами", 850.0))

        desserts.add(MenuItem("Тирамису", "Классический итальянский десерт с маскарпоне", 350.0))
        desserts.add(MenuItem("Чизкейк", "Нежный десерт на основе сливочного сыра", 300.0))
        desserts.add(MenuItem("Фруктовый салат", "Ассорти из свежих фруктов", 250.0))

        hot_drinks = MenuCategory("Горячие напитки", "Согревающие напитки")
        cold_drinks = MenuCategory("Холодные напитки", "Освежающие напитки")

        hot_drinks.add(MenuItem("Эспрессо", "Крепкий итальянский кофе", 150.0))
        hot_drinks.add(MenuItem("Капучино", "Кофе с молочной пенкой", 200.0))
        hot_drinks.add(MenuItem("Чай", "Черный или зеленый на выбор", 150.0))

        cold_drinks.add(MenuItem("Лимонад", "Домашний лимонад с мятой", 200.0))
        cold_drinks.add(MenuItem("Молочный коктейль", "Ванильный, шоколадный или клубничный", 250.0))
        cold_drinks.add(MenuItem("Минеральная вода", "Газированная или негазированная", 100.0))

        drinks.add(hot_drinks)
        drinks.add(cold_drinks)

        menu.add(appetizers)
        menu.add(main_courses)
        menu.add(desserts)
        menu.add(drinks)

        return menu

    # --- Menu ---

    def display_menu(self) -> str:
        return self.menu.display()

    def find_menu_item(self, item_name: str) -> Optional[MenuItem]:
        def search_in_category(category: MenuCategory, name: str) -> Optional[MenuItem]:
            for component in category.menu_components:
                if isinstance(component, MenuItem) and component.name == name:
                    return component
                elif isinstance(component, MenuCategory):
                    result = search_in_category(component, name)
                    if result:
                        return result
            return None

        return search_in_category(self.menu, item_name)

    # --- Orders ---

    def create_order(self, table_number: int) -> Order:
        order = self.order_manager.create_order(table_number)
        print(f"Создан новый заказ #{order.order_id} для стола {table_number}")
        return order

    def add_item_to_order(self, order_id: int, item_name: str, quantity: int = 1) -> bool:
        order = self.order_manager.get_order(order_id)
        if not order:
            print(f"Заказ #{order_id} не найден")
            return False

        menu_item = self.find_menu_item(item_name)
        if not menu_item:
            print(f"Позиция '{item_name}' не найдена в меню")
            return False

        order.add_item(menu_item, quantity)
        print(f"В заказ #{order_id} добавлено: {item_name} x{quantity}")
        return True

    def submit_order_to_kitchen(self, order_id: int) -> bool:
        order = self.order_manager.get_order(order_id)
        if not order:
            print(f"Заказ #{order_id} не найден")
            return False

        order.change_status("Готовится")
        self.notification_service.notify_kitchen_about_new_order(order)
        print(f"Заказ #{order_id} отправлен на кухню")
        return True

    def complete_order(self, order_id: int) -> bool:
        order = self.order_manager.get_order(order_id)
        if not order:
            print(f"Заказ #{order_id} не найден")
            return False

        order.change_status("Готов")
        self.notification_service.notify_waiters_about_order_status(order, "готов к подаче")
        print(f"Заказ #{order_id} готов к подаче")
        return True

    def deliver_order(self, order_id: int) -> bool:
        order = self.order_manager.get_order(order_id)
        if not order:
            print(f"Заказ #{order_id} не найден")
            return False

        order.change_status("Доставлен")
        print(f"Заказ #{order_id} доставлен клиенту")
        return True

    # --- Payment ---

    def process_payment(self, order_id: int, payment_type: str, details: Dict = None) -> bool:
        order = self.order_manager.get_order(order_id)
        if not order:
            print(f"Заказ #{order_id} не найден")
            return False

        if details is None:
            details = {}

        transaction_id = None

        if payment_type.lower() == "cash":
            transaction_id = self.payment_service.process_cash_payment(order)
        elif payment_type.lower() == "card":
            card_number = details.get("card_number", "")
            cardholder = details.get("cardholder", "")
            transaction_id = self.payment_service.process_card_payment(order, card_number, cardholder)
        elif payment_type.lower() == "online":
            method = details.get("method", "online")
            transaction_id = self.payment_service.process_online_payment(order, method)
        else:
            print(f"Неподдерживаемый тип оплаты: {payment_type}")
            return False

        if transaction_id:
            order.change_status("Завершен")
            print(f"Заказ #{order_id} оплачен и завершен. ID транзакции: {transaction_id}")
            return True
        else:
            print(f"Ошибка при обработке оплаты для заказа #{order_id}")
            return False

    # --- Reports ---

    def generate_sales_report(self, days: int = 30) -> str:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return self.report_service.generate_sales_report(start_date, end_date)

    def generate_inventory_report(self) -> str:
        inventory_data = self.inventory_adapter.get_all_inventory()
        return self.report_service.generate_inventory_report(inventory_data)

    def generate_financial_report(self, period: str = "текущий месяц") -> str:
        return self.report_service.generate_financial_report(period)

    # --- Inventory ---

    def check_inventory(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        return self.inventory_adapter.get_all_inventory()

    def update_inventory_item(self, category: str, name: str, quantity: float) -> bool:
        if category == "Продукты":
            return self.inventory_adapter.update_product(name, quantity)
        elif category == "Расходные материалы":
            return self.inventory_adapter.update_supply(name, int(quantity))
        else:
            print(f"Неизвестная категория инвентаря: {category}")
            return False

    def check_low_stock(self) -> List[Dict[str, Any]]:
        return self.inventory_adapter.get_low_stock_items()

    # --- Employees ---

    def get_all_staff(self) -> List[Dict[str, Any]]:
        return self.staff_adapter.get_all_staff()

    def get_staff_by_role(self, role: str) -> List[Dict[str, Any]]:
        return self.staff_adapter.get_staff_by_role(role)

    def get_staff_on_shift(self, date: str = None) -> List[Dict[str, Any]]:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return self.staff_adapter.get_staff_on_shift(date)

    def schedule_shift(self, staff_id: str, date: str, start_time: str, end_time: str) -> bool:
        return self.staff_adapter.schedule_shift(staff_id, date, start_time, end_time)
