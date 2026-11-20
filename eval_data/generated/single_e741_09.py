import random


def pick(options):
    l = "text"
    print(l.upper())
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
