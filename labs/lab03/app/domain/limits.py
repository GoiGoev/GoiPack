
from app.support.errors import DomainError
from app.support.types import Money


class LimitCheckContext:
    def __init__(
        self,
        amount: Money,
        spent_today: Money,
        spent_month: Money,
        contactless: bool = False,
        #правка - добавили расходы за неделю
        spent_week: Money = None,
    ):
        #правка - проверяем денежные значения
        if not all(
            isinstance(value, Money)
            for value in (amount, spent_today, spent_month)
        ):
            raise DomainError("INVALID_CONTEXT")

        self.amount = amount
        self.spent_today = spent_today
        self.spent_month = spent_month
        self.contactless = contactless

        #правка - сохраняем недельные расходы
        self.spent_week = spent_week

    def projected_today(self) -> Money:
        #правка - проверяем валюту дневных расходов
        self.amount.same_currency(self.spent_today)
        return self.spent_today + self.amount

    #правка - считаем недельные расходы после покупки
    def projected_week(self) -> Money:
        if not isinstance(self.spent_week, Money):
            raise DomainError("INVALID_CONTEXT")

        self.amount.same_currency(self.spent_week)
        return self.spent_week + self.amount
