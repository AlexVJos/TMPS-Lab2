from abc import ABC, abstractmethod
from typing import Dict
from models.order import Order


class PaymentProcessor(ABC):
    @abstractmethod
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        pass

    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        pass

    @abstractmethod
    def get_payment_status(self, transaction_id: str) -> str:
        pass


class CashPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        print(f"Обработка наличного платежа в размере {amount:.2f} лей.")
        return True

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        print(f"Возврат наличных в размере {amount:.2f} лей.")
        return True

    def get_payment_status(self, transaction_id: str) -> str:
        return "Оплачено наличными"


class CardPaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        card_number = payment_details.get("card_number", "")
        print(f"Обработка платежа картой {card_number[-4:]} в размере {amount:.2f} лей.")
        return True

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        print(f"Возврат средств на карту по транзакции {transaction_id} в размере {amount:.2f} лей.")
        return True

    def get_payment_status(self, transaction_id: str) -> str:
        return "Оплачено картой"


class OnlinePaymentProcessor(PaymentProcessor):
    def process_payment(self, amount: float, payment_details: Dict) -> bool:
        payment_method = payment_details.get("method", "онлайн")
        print(f"Обработка онлайн-платежа ({payment_method}) в размере {amount:.2f} лей.")
        return True

    def refund_payment(self, transaction_id: str, amount: float) -> bool:
        print(f"Возврат средств онлайн по транзакции {transaction_id} в размере {amount:.2f} лей.")
        return True

    def get_payment_status(self, transaction_id: str) -> str:
        return "Оплачено онлайн"


class PaymentInterface(ABC):
    def __init__(self, processor: PaymentProcessor):
        self.processor = processor

    @abstractmethod
    def pay_order(self, order: Order, payment_details: Dict) -> bool:
        pass

    @abstractmethod
    def refund_order(self, order: Order, transaction_id: str) -> bool:
        pass
