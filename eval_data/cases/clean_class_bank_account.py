class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def show(self):
        print(self.owner, "has", self.balance, "euros")


account = BankAccount("Mia", 50)
account.deposit(25)
account.show()
