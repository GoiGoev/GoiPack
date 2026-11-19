
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

        if spent_week is not None and not isinstance(spent_week, Money):
            raise DomainError("INVALID_CONTEXT")

        #правка - проверяем положительную сумму
        if amount.amount <= 0:
            raise DomainError("INVALID_AMOUNT")

        #правка - проверяем contactless
        if type(contactless) is not bool:
            raise DomainError("INVALID_CONTEXT")

        #правка - проверяем валюты
        amount.same_currency(spent_today)
        amount.same_currency(spent_month)

        if spent_week is not None:
            amount.same_currency(spent_week)

        #правка - проверяем согласованность расходов
        if spent_today.amount > spent_month.amount:
            raise DomainError("INVALID_CONTEXT")

        if spent_week is not None:
            if not (spent_today.amount <= spent_week.amount <= spent_month.amount):
                raise DomainError("INVALID_CONTEXT")

        #правка - свойства только для чтения
        self._amount = amount
        self._spent_today = spent_today
        self._spent_month = spent_month
        self._contactless = contactless
        self._spent_week = spent_week

    @property
    def amount(self):
        return self._amount

    @property
    def spent_today(self):
        return self._spent_today

    @property
    def spent_month(self):
        return self._spent_month

    @property
    def contactless(self):
        return self._contactless

    @property
    def spent_week(self):
        return self._spent_week

    def projected_today(self) -> Money:
        #правка - используем Money.add()
        self.amount.same_currency(self.spent_today)
        return self.spent_today.add(self.amount)

    #правка - считаем недельные расходы после покупки
    def projected_week(self) -> Money:
        if self.spent_week is None:
            return None

        self.amount.same_currency(self.spent_week)
        return self.spent_week.add(self.amount)
