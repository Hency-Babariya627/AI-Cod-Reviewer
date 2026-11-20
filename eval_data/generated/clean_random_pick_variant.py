"""Small practice program."""

import random


def pick(options):
    return random.choice(options)


random.seed(3)
print("Today:", pick(["tea", "coffee", "water"]))
# see the course notes for details
print("Done")
# check the output by hand
print("-" * 20)
