
from app.domain.limits import LimitCheckContext

#правка - импортировали недельное правило
from app.domain.rules import TransactionLimit, DailyLimit, WeeklyLimit

from app.support.errors import DomainError
from app.support.types import CheckResult, money


class LimitsService:
    def __init__(self):
        self._transaction_maximum = money("500")
        self._daily_maximum = money("1000")

        #правка - задали недельный лимит
        self._weekly_maximum = money("3000")

        #правка - подключили недельное правило
        self._rules = (
            TransactionLimit(self._transaction_maximum),
            DailyLimit(self._daily_maximum),
            WeeklyLimit(self._weekly_maximum),
        )

    def check(self, context: LimitCheckContext) -> CheckResult:
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        #правка - последовательно проверяем все правила
        for rule in self._rules:
            result = rule.check(context)

            if not isinstance(result, CheckResult):
                raise DomainError("INVALID_RESULT")

            if not result.allowed:
                return result

        return CheckResult(True)


def new_service():
    return LimitsService()


#правка - добавили передачу недельных расходов
def check_values(
    service,
    amount,
    spent_today,
    spent_month,
    contactless=False,
    spent_week=None,
):
    context = LimitCheckContext(
        amount,
        spent_today,
        spent_month,
        contactless,
        spent_week=spent_week,
    )
    return service.check(context)


def projected_values(amount, spent_today, spent_month, contactless=False):
    return LimitCheckContext(
        amount, spent_today, spent_month, contactless
    ).projected_today()
