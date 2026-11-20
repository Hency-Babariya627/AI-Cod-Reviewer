import random


def pick(options):
    print(f"----------")
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
