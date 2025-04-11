from abc import ABC, abstractmethod
from typing import List, Optional


class MenuComponent(ABC):
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    @abstractmethod
    def get_price(self) -> float:
        pass

    @abstractmethod
    def display(self, indent: int = 0) -> str:
        pass

    def add(self, component):
        raise NotImplementedError("Операция не поддерживается")

    def remove(self, component):
        raise NotImplementedError("Операция не поддерживается")

    def get_child(self, index: int):
        raise NotImplementedError("Операция не поддерживается")


class MenuItem(MenuComponent):
    def __init__(self, name: str, description: str, price: float):
        super().__init__(name, description)
        self.price = price

    def get_price(self) -> float:
        return self.price

    def display(self, indent: int = 0) -> str:
        return " " * indent + f"- {self.name}: {self.price:.2f} лей ({self.description})"


class MenuCategory(MenuComponent):
    def __init__(self, name: str, description: str = ""):
        super().__init__(name, description)
        self.menu_components: List[MenuComponent] = []

    def add(self, component: MenuComponent):
        self.menu_components.append(component)

    def remove(self, component: MenuComponent):
        self.menu_components.remove(component)

    def get_child(self, index: int) -> Optional[MenuComponent]:
        if 0 <= index < len(self.menu_components):
            return self.menu_components[index]
        return None

    def get_price(self) -> float:
        return sum(component.get_price() for component in self.menu_components)

    def display(self, indent: int = 0) -> str:
        result = " " * indent + f"{self.name}:" + ("\n" if self.menu_components else "")

        for component in self.menu_components:
            result += component.display(indent + 2) + "\n"

        return result.rstrip()
