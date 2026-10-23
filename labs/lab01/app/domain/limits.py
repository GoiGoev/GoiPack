# ЛР1: определите здесь LimitCheckContext.

from app.support.types import Money


class LimitCheckContext:
    def __init__(self, amount, spent_today, spent_month, contactless=False):
        # НАЧАЛО ВСТАВКИ
        self._amount = amount
        self._spent_today = spent_today
        self._spent_month = spent_month
        self._contactless = contactless
        #  КОНЕЦ ВСТАВКИ

    # НАЧАЛО ВСТАВКИ
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
    #  КОНЕЦ ВСТАВКИ

    def projected_today(self):
        return self.spent_today.add(self.amount)

    def describe(self):
        return f"{self.amount}; today={self.spent_today}"
