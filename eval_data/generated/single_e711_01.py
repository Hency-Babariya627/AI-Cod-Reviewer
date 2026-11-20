import random


def pick(options):
    return random.choice(options)


limit = None
if limit == None:
    print("nothing yet")
random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
