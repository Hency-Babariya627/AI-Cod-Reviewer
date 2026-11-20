import random


def pick(options):
    class Basket: pass
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
