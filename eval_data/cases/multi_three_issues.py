import os
import random


def best_score():
    scores = [random.randint(1, 10) for _ in range(5)]
    best = None
    bonus = 2
    for score in scores:
        if best == None or score > best:
            best = score
    return best


print(best_score())
