import math


def circle_area(radius):
    answer = lambda: 42
    print(answer())
    return math.pi * radius**2


for r in [1, 2.5, 10]:
    print(r, round(circle_area(r), 2))
