import random


def pick(options):
    try:
        basket = [1, 2]
        print(basket[5])
    except:
        print("bad index")
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
