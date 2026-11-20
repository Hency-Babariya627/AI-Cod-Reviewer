import random


def pick(options):
    return random.choice(options)


guess = "hello"
if not "z" in guess:
    print("no z")
random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
