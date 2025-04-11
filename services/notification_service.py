from abc import ABC, abstractmethod
from datetime import datetime
from models.order import Order


class NotificationService(ABC):
    @abstractmethod
    def notify(self, recipient: str, message: str) -> bool:
        pass


class BasicNotificationService(NotificationService):
    def notify(self, recipient: str, message: str) -> bool:
        print(f"[УВЕДОМЛЕНИЕ] Получатель: {recipient}")
        print(f"Сообщение: {message}")
        return True


class NotificationDecorator(NotificationService):
    def __init__(self, notification_service: NotificationService):
        self.wrapped_service = notification_service

    def notify(self, recipient: str, message: str) -> bool:
        return self.wrapped_service.notify(recipient, message)


class LoggingNotificationDecorator(NotificationDecorator):
    def __init__(self, notification_service: NotificationService, log_file: str = "notifications.log"):
        super().__init__(notification_service)
        self.log_file = log_file

    def notify(self, recipient: str, message: str) -> bool:
        result = self.wrapped_service.notify(recipient, message)

        print(f"[ЛОГ] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
              f"Отправлено уведомление для {recipient}")

        return result


class FormattingNotificationDecorator(NotificationDecorator):
    def __init__(self, notification_service: NotificationService, prefix: str = "", suffix: str = ""):
        super().__init__(notification_service)
        self.prefix = prefix
        self.suffix = suffix

    def notify(self, recipient: str, message: str) -> bool:
        formatted_message = f"{self.prefix}{message}{self.suffix}"
        return self.wrapped_service.notify(recipient, formatted_message)


class PriorityNotificationDecorator(NotificationDecorator):
    def __init__(self, notification_service: NotificationService, priority: str = "NORMAL"):
        super().__init__(notification_service)
        self.priority = priority

    def notify(self, recipient: str, message: str) -> bool:
        prioritized_message = f"[{self.priority}] {message}"
        return self.wrapped_service.notify(recipient, prioritized_message)


class StaffNotificationService:
    def __init__(self):
        base_service = BasicNotificationService()

        self.kitchen_service = FormattingNotificationDecorator(
            LoggingNotificationDecorator(base_service),
            prefix="[КУХНЯ] "
        )

        self.management_service = PriorityNotificationDecorator(
            FormattingNotificationDecorator(
                LoggingNotificationDecorator(base_service),
                prefix="[РУКОВОДСТВО] "
            ),
            priority="HIGH"
        )

        self.waiters_service = FormattingNotificationDecorator(
            LoggingNotificationDecorator(base_service),
            prefix="[ОФИЦИАНТЫ] "
        )

    def notify_kitchen_about_new_order(self, order: Order) -> bool:
        message = f"Новый заказ #{order.order_id} для стола {order.table_number}:\n"
        for item in order.items:
            message += f"  - {item.menu_item.name} x{item.quantity}\n"

        return self.kitchen_service.notify("kitchen", message)

    def notify_management_about_issue(self, issue_type: str, details: str) -> bool:
        message = f"Проблема: {issue_type}\nПодробности: {details}"
        return self.management_service.notify("management", message)

    def notify_waiters_about_order_status(self, order: Order, status: str) -> bool:
        message = f"Заказ #{order.order_id} для стола {order.table_number}: {status}"
        return self.waiters_service.notify("waiters", message)

    def notify_all_staff(self, message: str) -> bool:
        kitchen_result = self.kitchen_service.notify("kitchen", message)
        management_result = self.management_service.notify("management", message)
        waiters_result = self.waiters_service.notify("waiters", message)

        return kitchen_result and management_result and waiters_result
