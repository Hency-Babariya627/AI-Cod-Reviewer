import random


def pick(options):
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
