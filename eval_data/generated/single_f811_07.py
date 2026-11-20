import random


def pick(options):
    return random.choice(options)


def greet_user():
    print("-" * 20)


def greet_user():
    print("=" * 20)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
