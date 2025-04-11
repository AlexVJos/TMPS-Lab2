from typing import Dict, List
from interfaces.payment_interface import PaymentInterface, PaymentProcessor
from models.order import Order


class StandardPaymentInterface(PaymentInterface):
    def __init__(self, processor: PaymentProcessor):
        super().__init__(processor)
        self.transactions = {}

    def pay_order(self, order: Order, payment_details: Dict) -> bool:
        amount = order.get_total_price()
        success = self.processor.process_payment(amount, payment_details)

        if success:
            transaction_id = f"TRX-{len(self.transactions) + 1}"

            self.transactions[transaction_id] = {
                "order_id": order.order_id,
                "amount": amount,
                "details": payment_details,
                "timestamp": order.creation_time
            }

            payment_method = self._get_payment_method_name()
            order.mark_as_paid(payment_method)

            return transaction_id

        return None

    def refund_order(self, order: Order, transaction_id: str) -> bool:
        if transaction_id not in self.transactions:
            return False

        transaction = self.transactions[transaction_id]
        if transaction["order_id"] != order.order_id:
            return False

        success = self.processor.refund_payment(transaction_id, transaction["amount"])

        if success:
            order.payment_status = "Refunded"
            return True

        return False

    def _get_payment_method_name(self) -> str:
        processor_class = self.processor.__class__.__name__
        if "Cash" in processor_class:
            return "Наличные"
        elif "Card" in processor_class:
            return "Карта"
        elif "Online" in processor_class:
            return "Онлайн"
        else:
            return "Неизвестный метод"

    def get_transaction_history(self) -> List[Dict]:
        return [
            {**details, "transaction_id": tx_id}
            for tx_id, details in self.transactions.items()
       ]


class PaymentService:
    def __init__(self):
        from interfaces.payment_interface import (
            CashPaymentProcessor,
            CardPaymentProcessor,
            OnlinePaymentProcessor
        )

        self.cash_interface = StandardPaymentInterface(CashPaymentProcessor())
        self.card_interface = StandardPaymentInterface(CardPaymentProcessor())
        self.online_interface = StandardPaymentInterface(OnlinePaymentProcessor())

    def process_cash_payment(self, order: Order) -> bool:
        return self.cash_interface.pay_order(order, {"method": "cash"})

    def process_card_payment(self, order: Order, card_number: str, cardholder: str) -> bool:
        payment_details = {
            "method": "card",
            "card_number": card_number,
            "cardholder": cardholder
        }
        return self.card_interface.pay_order(order, payment_details)

    def process_online_payment(self, order: Order, payment_method: str) -> bool:
        payment_details = {
            "method": payment_method
        }
        return self.online_interface.pay_order(order, payment_details)

    def refund_payment(self, order: Order, transaction_id: str) -> bool:
        if "Наличные" in order.payment_status:
            return self.cash_interface.refund_order(order, transaction_id)
        elif "Карта" in order.payment_status:
            return self.card_interface.refund_order(order, transaction_id)
        elif "Онлайн" in order.payment_status:
            return self.online_interface.refund_order(order, transaction_id)
        else:
            return False

    def get_transaction_history(self) -> List[Dict]:
        cash_transactions = self.cash_interface.get_transaction_history()
        card_transactions = self.card_interface.get_transaction_history()
        online_transactions = self.online_interface.get_transaction_history()

        return cash_transactions + card_transactions + online_transactions
