
from app.domain.limits import LimitCheckContext

#правка - импортировали правила для использования в сервисе
from app.domain.rules import TransactionLimit, DailyLimit
#правка - импортировали ошибку для некорректного контекста или результата
from app.support.errors import DomainError

from app.support.types import CheckResult, money


class LimitsService:
    def __init__(self):
        self._transaction_maximum = money("500")
        self._daily_maximum = money("1000")

        #правка - создали правила и задали порядок их проверки
        self._rules = (
            TransactionLimit(self._transaction_maximum),
            DailyLimit(self._daily_maximum),
        )

    def check(self, context: LimitCheckContext) -> CheckResult:
        #правка - проверяем тип переданного контекста
        if not isinstance(context, LimitCheckContext):
            raise DomainError("INVALID_CONTEXT")

        #правка - вызываем каждое правило через общий интерфейс
        for rule in self._rules:
            result = rule.check(context)

            #правка - проверяем тип результата каждого правила
            if not isinstance(result, CheckResult):
                raise DomainError("INVALID_RESULT")

            #правка - возвращаем первый отказ по порядку правил
            if not result.allowed:
                return result

        #правка - если все правила разрешили покупку, возвращаем успех
        return CheckResult(True)


def new_service():
    return LimitsService()


def check_values(service, amount, spent_today, spent_month, contactless=False):
    context = LimitCheckContext(amount, spent_today, spent_month, contactless)
    return service.check(context)


def projected_values(amount, spent_today, spent_month, contactless=False):
    return LimitCheckContext(
        amount, spent_today, spent_month, contactless
    ).projected_today()
