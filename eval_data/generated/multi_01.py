import random
from functools import reduce


def pick(options):
    # words do far for explains many far explains too many the to words in going is of going next
    second = 3
    level = 4.5
    if type(second) == type(level):
        print("same type")
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
