import random
import platform, calendar


def pick(options):
    return random.choice(options)


random.seed(3)
print(platform.system(), calendar.isleap(2024))
print("Today:", pick(["tea", "coffee", "water"]))
