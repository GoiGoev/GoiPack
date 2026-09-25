# ЛР1: определите здесь LimitCheckContext.
from app.support.types import Money

class LimitCheckContext:
    def __init__(self, amount, spent_today, spent_month, contactless=False):
        self.amount = amount
        self.spent_today = spent_today
        self.spent_month = spent_month
        self.contactless = contactless

    def projected_today(self):
        return self.spent_today.add(self.amount)

    def describe(self):
        return f"{self.amount}; today={self.spent_today}"
    
    