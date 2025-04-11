from typing import Dict, List, Any


class LegacyInventorySystem:
    def __init__(self):
        self._inventory = {
            "products": {
                "tomatoes": {"qty": 5.5, "unit": "kg", "min_qty": 3.0},
                "potatoes": {"qty": 10.0, "unit": "kg", "min_qty": 5.0},
                "onions": {"qty": 3.0, "unit": "kg", "min_qty": 2.0},
                "beef": {"qty": 7.0, "unit": "kg", "min_qty": 2.0},
                "chicken": {"qty": 8.5, "unit": "kg", "min_qty": 3.0}
            },
            "supplies": {
                "napkins": {"qty": 200, "unit": "pcs", "min_qty": 100},
                "takeout_boxes": {"qty": 50, "unit": "pcs", "min_qty": 20},
                "plastic_utensils": {"qty": 150, "unit": "pcs", "min_qty": 50}
            }
        }

    def get_product_quantity(self, product_name: str) -> float:
        if product_name in self._inventory["products"]:
            return self._inventory["products"][product_name]["qty"]
        return 0.0

    def update_product_quantity(self, product_name: str, new_qty: float) -> bool:
        if product_name in self._inventory["products"]:
            self._inventory["products"][product_name]["qty"] = new_qty
            return True
        return False

    def get_supply_quantity(self, supply_name: str) -> int:
        if supply_name in self._inventory["supplies"]:
            return self._inventory["supplies"][supply_name]["qty"]
        return 0

    def update_supply_quantity(self, supply_name: str, new_qty: int) -> bool:
        if supply_name in self._inventory["supplies"]:
            self._inventory["supplies"][supply_name]["qty"] = new_qty
            return True
        return False


class InventoryAdapter:
    def __init__(self, legacy_system: LegacyInventorySystem):
        self.legacy_system = legacy_system

    def get_all_inventory(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        result = {
            "Продукты": {},
            "Расходные материалы": {}
        }

        for product_name, product_data in self.legacy_system._inventory["products"].items():
            result["Продукты"][product_name] = {
                "quantity": product_data["qty"],
                "unit": product_data["unit"],
                "min_quantity": product_data["min_qty"]
            }

        for supply_name, supply_data in self.legacy_system._inventory["supplies"].items():
            result["Расходные материалы"][supply_name] = {
                "quantity": supply_data["qty"],
                "unit": supply_data["unit"],
                "min_quantity": supply_data["min_qty"]
            }

        return result

    def update_product(self, name: str, quantity: float) -> bool:
        return self.legacy_system.update_product_quantity(name, quantity)

    def update_supply(self, name: str, quantity: int) -> bool:
        return self.legacy_system.update_supply_quantity(name, quantity)

    def get_low_stock_items(self) -> List[Dict[str, Any]]:
        low_stock = []
        inventory = self.get_all_inventory()

        for name, data in inventory["Продукты"].items():
            if data["quantity"] < data["min_quantity"]:
                low_stock.append({
                    "name": name,
                    "category": "Продукты",
                    "current": data["quantity"],
                    "minimum": data["min_quantity"],
                    "unit": data["unit"]
                })

        for name, data in inventory["Расходные материалы"].items():
            if data["quantity"] < data["min_quantity"]:
                low_stock.append({
                    "name": name,
                    "category": "Расходные материалы",
                    "current": data["quantity"],
                    "minimum": data["min_quantity"],
                    "unit": data["unit"]
                })

        return low_stock

    def use_product_for_order(self, product_name: str, quantity: float) -> bool:
        current_qty = self.legacy_system.get_product_quantity(product_name)
        if current_qty >= quantity:
            new_qty = current_qty - quantity
            return self.legacy_system.update_product_quantity(product_name, new_qty)
        return False


class LegacyEmployeeSystem:
    def __init__(self):
        self._employees = {
            "1": {"name": "Иванов Иван", "position": "Шеф-повар", "salary": 70000},
            "2": {"name": "Петров Петр", "position": "Повар", "salary": 45000},
            "3": {"name": "Сидорова Анна", "position": "Официант", "salary": 35000},
            "4": {"name": "Кузнецов Алексей", "position": "Официант", "salary": 35000},
            "5": {"name": "Новикова Елена", "position": "Администратор", "salary": 50000}
        }

        self._shifts = {
            "1": [{"date": "2025-04-10", "start": "08:00", "end": "16:00"}],
            "2": [{"date": "2025-04-10", "start": "16:00", "end": "00:00"}],
            "3": [{"date": "2025-04-10", "start": "10:00", "end": "18:00"}],
            "4": [{"date": "2025-04-10", "start": "18:00", "end": "02:00"}],
            "5": [{"date": "2025-04-10", "start": "10:00", "end": "19:00"}]
        }

    def get_employee(self, emp_id: str) -> Dict:
        return self._employees.get(emp_id, {})

    def get_employee_shifts(self, emp_id: str) -> List[Dict]:
        return self._shifts.get(emp_id, [])

    def add_shift(self, emp_id: str, date: str, start: str, end: str) -> bool:
        if emp_id in self._employees:
            if emp_id not in self._shifts:
                self._shifts[emp_id] = []

            self._shifts[emp_id].append({
                "date": date,
                "start": start,
                "end": end
            })
            return True
        return False


class StaffAdapter:
    def __init__(self, legacy_system: LegacyEmployeeSystem):
        self.legacy_system = legacy_system

    def get_all_staff(self) -> List[Dict[str, Any]]:
        result = []

        for emp_id, emp_data in self.legacy_system._employees.items():
            shifts = self.legacy_system.get_employee_shifts(emp_id)

            staff_member = {
                "id": emp_id,
                "name": emp_data["name"],
                "role": emp_data["position"],
                "salary": emp_data["salary"],
                "shifts": shifts
            }

            result.append(staff_member)

        return result

    def get_staff_by_role(self, role: str) -> List[Dict[str, Any]]:
        all_staff = self.get_all_staff()
        return [staff for staff in all_staff if staff["role"] == role]

    def get_staff_on_shift(self, date: str) -> List[Dict[str, Any]]:
        all_staff = self.get_all_staff()
        result = []

        for staff in all_staff:
            for shift in staff["shifts"]:
                if shift["date"] == date:
                    result.append({
                        "id": staff["id"],
                        "name": staff["name"],
                        "role": staff["role"],
                        "shift_start": shift["start"],
                        "shift_end": shift["end"]
                    })
                    break

        return result

    def schedule_shift(self, staff_id: str, date: str, start_time: str, end_time: str) -> bool:
        return self.legacy_system.add_shift(staff_id, date, start_time, end_time)
