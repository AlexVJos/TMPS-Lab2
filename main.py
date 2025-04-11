import os
import time
from datetime import datetime

from facade.restaurant_facade import RestaurantFacade


class ConsoleUI:
    def __init__(self):
        self.facade = RestaurantFacade()
        self.running = True

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        print("=" * 80)
        print("                        СИСТЕМА УПРАВЛЕНИЯ РЕСТОРАНОМ")
        print("=" * 80)
        print(f"Дата: {datetime.now().strftime('%Y-%m-%d')}")
        print(f"Время: {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 80)

    def display_main_menu(self):
        self.clear_screen()
        self.display_header()

        print("ГЛАВНОЕ МЕНЮ:")
        print("1. Управление меню")
        print("2. Управление заказами")
        print("3. Управление инвентарем")
        print("4. Управление персоналом")
        print("5. Отчеты")
        print("0. Выход")
        print("-" * 80)

    def handle_menu_management(self):
        self.clear_screen()
        self.display_header()

        print("УПРАВЛЕНИЕ МЕНЮ:")
        print("1. Показать всё меню")
        print("0. Назад")
        print("-" * 80)

        choice = input("Выберите действие: ")

        if choice == "1":
            self.clear_screen()
            self.display_header()
            print("МЕНЮ РЕСТОРАНА:")
            print("-" * 80)
            print(self.facade.display_menu())
            print("-" * 80)
            input("Нажмите Enter для возврата...")

    def handle_order_management(self):
        while True:
            self.clear_screen()
            self.display_header()

            print("УПРАВЛЕНИЕ ЗАКАЗАМИ:")
            print("1. Показать активные заказы")
            print("2. Создать новый заказ")
            print("3. Добавить позиции в заказ")
            print("4. Отправить заказ на кухню")
            print("5. Пометить заказ как готовый")
            print("6. Доставить заказ клиенту")
            print("7. Обработать оплату заказа")
            print("0. Назад")
            print("-" * 80)

            choice = input("Выберите действие: ")

            if choice == "0":
                break
            elif choice == "1":
                # Показать активные заказы
                active_orders = self.facade.order_manager.get_active_orders()
                self.clear_screen()
                self.display_header()
                print("АКТИВНЫЕ ЗАКАЗЫ:")
                print("-" * 80)

                if not active_orders:
                    print("Активные заказы отсутствуют")
                else:
                    for order in active_orders:
                        print(order)
                        print("-" * 80)

                input("Нажмите Enter для возврата...")

            elif choice == "2":
                try:
                    table_number = int(input("Введите номер стола: "))
                    order = self.facade.create_order(table_number)
                    print(f"Создан заказ #{order.order_id} для стола {table_number}")
                    time.sleep(1)
                except ValueError:
                    print("Некорректный номер стола")
                    time.sleep(1)

            elif choice == "3":
                try:
                    order_id = int(input("Введите номер заказа: "))
                    order = self.facade.order_manager.get_order(order_id)

                    if not order:
                        print(f"Заказ #{order_id} не найден")
                        time.sleep(1)
                        continue

                    self.clear_screen()
                    self.display_header()
                    print(f"ДОБАВЛЕНИЕ ПОЗИЦИЙ В ЗАКАЗ #{order_id}:")
                    print("-" * 80)
                    print(self.facade.display_menu())
                    print("-" * 80)

                    while True:
                        item_name = input("Введите название блюда (или 'готово' для завершения): ")

                        if item_name.lower() == "готово":
                            break

                        menu_item = self.facade.find_menu_item(item_name)
                        if not menu_item:
                            print(f"Позиция '{item_name}' не найдена в меню")
                            continue

                        try:
                            quantity = int(input("Введите количество: "))
                            if quantity <= 0:
                                print("Количество должно быть положительным числом")
                                continue

                            self.facade.add_item_to_order(order_id, item_name, quantity)
                        except ValueError:
                            print("Некорректное количество")

                except ValueError:
                    print("Некорректный номер заказа")
                    time.sleep(1)

            elif choice == "4":
                try:
                    order_id = int(input("Введите номер заказа: "))
                    if self.facade.submit_order_to_kitchen(order_id):
                        print(f"Заказ #{order_id} отправлен на кухню")
                    time.sleep(1)
                except ValueError:
                    print("Некорректный номер заказа")
                    time.sleep(1)

            elif choice == "5":
                try:
                    order_id = int(input("Введите номер заказа: "))
                    if self.facade.complete_order(order_id):
                        print(f"Заказ #{order_id} помечен как готовый")
                    time.sleep(1)
                except ValueError:
                    print("Некорректный номер заказа")
                    time.sleep(1)

            elif choice == "6":
                try:
                    order_id = int(input("Введите номер заказа: "))
                    if self.facade.deliver_order(order_id):
                        print(f"Заказ #{order_id} доставлен клиенту")
                    time.sleep(1)
                except ValueError:
                    print("Некорректный номер заказа")
                    time.sleep(1)

            elif choice == "7":
                try:
                    order_id = int(input("Введите номер заказа: "))
                    order = self.facade.order_manager.get_order(order_id)

                    if not order:
                        print(f"Заказ #{order_id} не найден")
                        time.sleep(1)
                        continue

                    print(f"Сумма заказа: {order.get_total_price():.2f} лей.")
                    payment_type = input("Выберите тип оплаты (cash/card/online): ").lower()

                    details = {}
                    if payment_type == "card":
                        details["card_number"] = input("Введите номер карты: ")
                        details["cardholder"] = input("Введите имя владельца карты: ")
                    elif payment_type == "online":
                        details["method"] = input("Введите метод онлайн-оплаты: ")

                    if self.facade.process_payment(order_id, payment_type, details):
                        print(f"Заказ #{order_id} успешно оплачен")
                    time.sleep(1)
                except ValueError:
                    print("Некорректный номер заказа")
                    time.sleep(1)

    def handle_inventory_management(self):
        while True:
            self.clear_screen()
            self.display_header()

            print("УПРАВЛЕНИЕ ИНВЕНТАРЕМ:")
            print("1. Показать текущий инвентарь")
            print("2. Обновить количество товара")
            print("3. Проверить товары с низким запасом")
            print("0. Назад")
            print("-" * 80)

            choice = input("Выберите действие: ")

            if choice == "0":
                break
            elif choice == "1":
                # Показать текущий инвентарь
                inventory = self.facade.check_inventory()
                self.clear_screen()
                self.display_header()
                print("ТЕКУЩИЙ ИНВЕНТАРЬ:")
                print("-" * 80)

                for category, items in inventory.items():
                    print(f"\n{category}:")
                    for name, data in items.items():
                        print(f"  {name}: {data['quantity']} {data['unit']} "
                              f"(мин. запас: {data['min_quantity']})")

                print("-" * 80)
                input("Нажмите Enter для возврата...")

            elif choice == "2":
                # Обновить количество товара
                self.clear_screen()
                self.display_header()
                print("ОБНОВЛЕНИЕ КОЛИЧЕСТВА ТОВАРА:")
                print("-" * 80)

                inventory = self.facade.check_inventory()
                categories = list(inventory.keys())

                print("Доступные категории:")
                for i, category in enumerate(categories, 1):
                    print(f"{i}. {category}")

                try:
                    cat_idx = int(input("Выберите категорию (номер): ")) - 1
                    if cat_idx < 0 or cat_idx >= len(categories):
                        print("Некорректный номер категории")
                        time.sleep(1)
                        continue

                    category = categories[cat_idx]
                    print(f"\nТовары в категории '{category}':")
                    items = list(inventory[category].keys())
                    for i, item_name in enumerate(items, 1):
                        data = inventory[category][item_name]
                        print(f"{i}. {item_name}: {data['quantity']} {data['unit']}")

                    item_idx = int(input("Выберите товар (номер): ")) - 1
                    if item_idx < 0 or item_idx >= len(items):
                        print("Некорректный номер товара")
                        time.sleep(1)
                        continue

                    item_name = items[item_idx]
                    current_qty = inventory[category][item_name]['quantity']

                    print(
                        f"Текущее количество {item_name}: {current_qty} {inventory[category][item_name]['unit']}")
                    new_qty = float(input("Введите новое количество: "))

                    if self.facade.update_inventory_item(category, item_name, new_qty):
                        print(f"Количество {item_name} обновлено на {new_qty}")
                    else:
                        print(f"Ошибка при обновлении количества {item_name}")

                    time.sleep(1)
                except ValueError:
                    print("Некорректный ввод")
                    time.sleep(1)

            elif choice == "3":
                # Проверить товары с низким запасом
                low_stock = self.facade.check_low_stock()
                self.clear_screen()
                self.display_header()
                print("ТОВАРЫ С НИЗКИМ ЗАПАСОМ:")
                print("-" * 80)

                if not low_stock:
                    print("Нет товаров с низким запасом")
                else:
                    for item in low_stock:
                        print(f"{item['name']} ({item['category']}): "
                              f"{item['current']} {item['unit']} "
                              f"(мин. запас: {item['minimum']} {item['unit']})")

                print("-" * 80)
                input("Нажмите Enter для возврата...")

    def handle_staff_management(self):
        """Обработка раздела управления персоналом"""
        while True:
            self.clear_screen()
            self.display_header()

            print("УПРАВЛЕНИЕ ПЕРСОНАЛОМ:")
            print("1. Показать всех сотрудников")
            print("2. Показать сотрудников по должности")
            print("3. Показать сотрудников на смене")
            print("4. Запланировать смену")
            print("0. Назад")
            print("-" * 80)

            choice = input("Выберите действие: ")

            if choice == "0":
                break
            elif choice == "1":
                # Показать всех сотрудников
                staff = self.facade.get_all_staff()
                self.clear_screen()
                self.display_header()
                print("СПИСОК СОТРУДНИКОВ:")
                print("-" * 80)

                for employee in staff:
                    print(f"ID: {employee['id']}")
                    print(f"Имя: {employee['name']}")
                    print(f"Должность: {employee['role']}")
                    print(f"Зарплата: {employee['salary']} лей.")
                    print("-" * 40)

                input("Нажмите Enter для возврата...")

            elif choice == "2":
                # Показать сотрудников по должности
                role = input("Введите должность: ")
                staff = self.facade.get_staff_by_role(role)

                self.clear_screen()
                self.display_header()
                print(f"СОТРУДНИКИ С ДОЛЖНОСТЬЮ '{role}':")
                print("-" * 80)

                if not staff:
                    print(f"Сотрудники с должностью '{role}' не найдены")
                else:
                    for employee in staff:
                        print(f"ID: {employee['id']}")
                        print(f"Имя: {employee['name']}")
                        print(f"Зарплата: {employee['salary']} лей.")
                        print("-" * 40)

                input("Нажмите Enter для возврата...")

            elif choice == "3":
                # Показать сотрудников на смене
                date = input("Введите дату (ГГГГ-ММ-ДД) или оставьте пустым для текущей даты: ")
                if not date:
                    date = datetime.now().strftime("%Y-%m-%d")

                staff = self.facade.get_staff_on_shift(date)

                self.clear_screen()
                self.display_header()
                print(f"СОТРУДНИКИ НА СМЕНЕ {date}:")
                print("-" * 80)

                if not staff:
                    print(f"Сотрудники на смене {date} не найдены")
                else:
                    for employee in staff:
                        print(f"ID: {employee['id']}")
                        print(f"Имя: {employee['name']}")
                        print(f"Должность: {employee['role']}")
                        print(f"Время смены: {employee['shift_start']} - {employee['shift_end']}")
                        print("-" * 40)

                input("Нажмите Enter для возврата...")

            elif choice == "4":
                # Запланировать смену
                try:
                    staff_id = input("Введите ID сотрудника: ")
                    date = input("Введите дату (ГГГГ-ММ-ДД): ")
                    start_time = input("Введите время начала (ЧЧ:ММ): ")
                    end_time = input("Введите время окончания (ЧЧ:ММ): ")

                    if self.facade.schedule_shift(staff_id, date, start_time, end_time):
                        print(f"Смена для сотрудника {staff_id} запланирована на {date}")
                    else:
                        print(f"Ошибка при планировании смены для сотрудника {staff_id}")

                    time.sleep(1)
                except ValueError:
                    print("Некорректный ввод")
                    time.sleep(1)

    def handle_reports(self):
        """Обработка раздела отчетов"""
        while True:
            self.clear_screen()
            self.display_header()

            print("ОТЧЕТЫ:")
            print("1. Отчет по продажам")
            print("2. Отчет по инвентарю")
            print("3. Финансовый отчет")
            print("0. Назад")
            print("-" * 80)

            choice = input("Выберите действие: ")

            if choice == "0":
                break
            elif choice == "1":
                # Отчет по продажам
                try:
                    days = int(input("Введите количество дней для отчета (по умолчанию 30): ") or "30")
                    report = self.facade.generate_sales_report(days)

                    self.clear_screen()
                    self.display_header()
                    print(report)
                    print("-" * 80)
                    input("Нажмите Enter для возврата...")
                except ValueError:
                    print("Некорректный ввод")
                    time.sleep(1)

            elif choice == "2":
                # Отчет по инвентарю
                report = self.facade.generate_inventory_report()

                self.clear_screen()
                self.display_header()
                print(report)
                print("-" * 80)
                input("Нажмите Enter для возврата...")

            elif choice == "3":
                # Финансовый отчет
                period = input("Введите период отчета (по умолчанию 'текущий месяц'): ") or "текущий месяц"
                report = self.facade.generate_financial_report(period)

                self.clear_screen()
                self.display_header()
                print(report)
                print("-" * 80)
                input("Нажмите Enter для возврата...")

    def run(self):
        """Запустить пользовательский интерфейс"""
        while self.running:
            self.display_main_menu()
            choice = input("Выберите раздел: ")

            if choice == "0":
                self.running = False
            elif choice == "1":
                self.handle_menu_management()
            elif choice == "2":
                self.handle_order_management()
            elif choice == "3":
                self.handle_inventory_management()
            elif choice == "4":
                self.handle_staff_management()
            elif choice == "5":
                self.handle_reports()
            else:
                print("Некорректный выбор. Пожалуйста, выберите допустимый вариант.")
                time.sleep(1)


if __name__ == "__main__":
    ui = ConsoleUI()
    ui.run()
