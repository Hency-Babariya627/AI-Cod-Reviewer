import math


def circle_area(radius):
    return math.pi * radius**2


print("Digit:", "\d")
for r in [1, 2.5, 10]:
    print(r, round(circle_area(r), 2))
