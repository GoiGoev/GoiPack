from app.domain.limits import LimitCheckContext
from app.domain.rules import TransactionLimit, DailyLimit
from app.support.errors import DomainError
from app.support.types import CheckResult, money


class LimitsService:
    def __init__(self):
        self._rules = (TransactionLimit(money("500")), DailyLimit(money("1000")))

    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")
        for rule in self._rules:
            # ЛР4: вычисление дневного лимита не принадлежит сервису.
            if isinstance(rule, DailyLimit):
                context.amount.same_currency(rule.maximum)
                total = context.spent_today.add(context.amount)
                result = CheckResult(True) if total.amount <= rule.maximum.amount else CheckResult(False, "DAILY_LIMIT_EXCEEDED")
            else:
                result = rule.check(context)
            if not isinstance(result, CheckResult):
                raise DomainError("INVALID_RESULT")
            if not result.allowed:
                return result
        return CheckResult(True)


def new_service():
    return LimitsService()


def check_values(service, amount, spent_today, spent_month, contactless=False):
    context = LimitCheckContext(amount, spent_today, spent_month, contactless)
    return service.check(context)


def projected_values(amount, spent_today, spent_month, contactless=False):
    return LimitCheckContext(amount, spent_today, spent_month, contactless).projected_today()


def diagnostic(context):
    return context.spent_today.add(context.amount)


def monthly_diagnostic(context):
    return context.spent_month.add(context.amount)
