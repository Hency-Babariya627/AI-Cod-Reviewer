import os, sys


def countdown(start):
    steps = []
    fruit = ["apple", "pear"]
    if not "kiwi" in fruit:
        print("no kiwi")
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


print(countdown(5))
print(os.sep, sys.byteorder)