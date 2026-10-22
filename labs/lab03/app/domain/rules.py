
#правка - добавили инструменты для создания абстрактного класса
from abc import ABC, abstractmethod

from app.support.errors import DomainError
from app.support.types import Money, CheckResult
from app.domain.limits import LimitCheckContext


#правка - добавили ABC, чтобы общий класс нельзя было использовать без реализации check()
class LimitRule(ABC):
    def __init__(self, maximum: Money):
        if not isinstance(maximum, Money):
            raise DomainError("INVALID_CONFIG")
        self._maximum = maximum

    @property
    def maximum(self):
        return self._maximum

    # ЛР3: оформить ABC и общий контракт результата.
    #правка - сделали check() обязательным методом для наследников
    @abstractmethod
    def check(self, context: LimitCheckContext) -> CheckResult:
        pass


class TransactionLimit(LimitRule):
    # Перенести существующее транзакционное ограничение.
    #правка - добавили параметр code для бонусного задания
    def __init__(
        self,
        maximum: Money,
        code: str = "TRANSACTION_LIMIT_EXCEEDED",
    ):
        super().__init__(maximum)

        #правка - проверяем, что код ошибки не пустой
        if not isinstance(code, str) or not code.strip():
            raise DomainError("INVALID_CONFIG")
        self._code = code

    #правка - проверяем, что сумма покупки не превышает максимум
    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        self.maximum.same_currency(context.amount)

        if context.amount.amount > self.maximum.amount:
            return CheckResult(False, self._code)

        return CheckResult(True)


class DailyLimit(LimitRule):
    # Перенести существующее дневное ограничение.
    #правка - проверяем общие расходы за день с учётом текущей покупки
    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        projected = context.projected_today()
        self.maximum.same_currency(projected)

        if projected.amount > self.maximum.amount:
            return CheckResult(False, "DAILY_LIMIT_EXCEEDED")

        return CheckResult(True)
