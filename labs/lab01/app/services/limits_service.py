from app.support.types import CheckResult, money
from app.domain.limits import LimitCheckContext


class TransactionLimit:
    """Ограничение на одну покупку. Равенство допустимо."""

    def __init__(self, maximum):
        self._maximum = maximum

    def check(self, context):
        context.amount.same_currency(self._maximum)
        if context.amount.amount > self._maximum.amount:
            return CheckResult(False, "TRANSACTION_LIMIT_EXCEEDED")
        return CheckResult(True)


class DailyLimit:
    """Ограничение на сумму дня с учётом покупки. Равенство допустимо."""

    def __init__(self, maximum):
        self._maximum = maximum

    def check(self, context):
        projected = context.projected_today()
        projected.same_currency(self._maximum)
        if projected.amount > self._maximum.amount:
            return CheckResult(False, "DAILY_LIMIT_EXCEEDED")
        return CheckResult(True)


class LimitsService:
    """Проверяет лимиты по упорядоченному набору правил.

    По умолчанию: одна покупка ≤ 500 EUR, день с учётом покупки ≤ 1000 EUR.
    Возвращает первый отказ. Контекст не мутирует.
    """

    def __init__(self, rules=None):
        if rules is None:
            rules = [
                TransactionLimit(money("500")),
                DailyLimit(money("1000")),
            ]
        self._rules = tuple(rules)

    @property
    def rules(self):
        return self._rules

    def check(self, context):
        for rule in self._rules:
            result = rule.check(context)
            if not result.allowed:
                return result
        return CheckResult(True)


def new_service():
    return LimitsService()


def check_values(service, amount, spent_today, spent_month, contactless=False):
    context = LimitCheckContext(
        amount=amount,
        spent_today=spent_today,
        spent_month=spent_month,
        contactless=contactless,
    )
    return service.check(context)


def projected_values(amount, spent_today, spent_month, contactless=False):
    context = LimitCheckContext(
        amount=amount,
        spent_today=spent_today,
        spent_month=spent_month,
        contactless=contactless,
    )
    return context.projected_today()

def new_service():
    return {"transaction_maximum": money("500"), "daily_maximum": money("1000")}


def check_values(service, amount, spent_today, spent_month, contactless=False):
    context = {"amount": amount, "spent_today": spent_today,
               "spent_month": spent_month, "contactless": contactless}
    amount.same_currency(service["transaction_maximum"])
    amount.same_currency(service["daily_maximum"])
    if context["amount"].amount > service["transaction_maximum"].amount:
        return CheckResult(False, "TRANSACTION_LIMIT_EXCEEDED")
    projected = context["spent_today"].add(context["amount"])
    if projected.amount > service["daily_maximum"].amount:
        return CheckResult(False, "DAILY_LIMIT_EXCEEDED")
    return CheckResult(True)


def projected_values(amount, spent_today, spent_month, contactless=False):
    return spent_today.add(amount)
