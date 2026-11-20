from itertools import chain


def format_money(amount):
    return f"{amount:.2f} EUR"


class Account:
    def __init__(self, owner):
        self.owner = owner
        self.balance = 0

    def deposit(self, amount):
        self.balance += amount

    def describe(self):
        return f"{self.owner} has {format_money(self.balance)}"


account = Account("Ada")
account.deposit(50)
print(account.describe())
