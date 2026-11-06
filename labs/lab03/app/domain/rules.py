
from abc import ABC, abstractmethod

from app.support.errors import DomainError
from app.support.types import Money, CheckResult
from app.domain.limits import LimitCheckContext


class LimitRule(ABC):
    def __init__(self, maximum: Money):
        if not isinstance(maximum, Money):
            raise DomainError("INVALID_CONFIG")
        self._maximum = maximum

    @property
    def maximum(self):
        return self._maximum

    #правка - общий контракт для всех правил
    @abstractmethod
    def check(self, context: LimitCheckContext) -> CheckResult:
        pass


class TransactionLimit(LimitRule):
    def __init__(
        self,
        maximum: Money,
        code: str = "TRANSACTION_LIMIT_EXCEEDED",
    ):
        super().__init__(maximum)

        #правка - проверяем код отказа
        if not isinstance(code, str) or not code.strip():
            raise DomainError("INVALID_CONFIG")

        self._code = code

    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        self.maximum.same_currency(context.amount)

        if context.amount.amount > self.maximum.amount:
            return CheckResult(False, self._code)

        return CheckResult(True)


class DailyLimit(LimitRule):
    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        projected = context.projected_today()
        self.maximum.same_currency(projected)

        if projected.amount > self.maximum.amount:
            return CheckResult(False, "DAILY_LIMIT_EXCEEDED")

        return CheckResult(True)


#правка - новое правило проверки недельного лимита
class WeeklyLimit(LimitRule):
    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        #правка - получаем недельные расходы с учётом покупки
        projected = context.projected_week()
        self.maximum.same_currency(projected)

        #правка - отклоняем покупку при превышении лимита
        if projected.amount > self.maximum.amount:
            return CheckResult(False, "WEEKLY_LIMIT_EXCEEDED")

        return CheckResult(True)
