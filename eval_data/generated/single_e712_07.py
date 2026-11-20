import math


def circle_area(radius):
    return math.pi * radius**2


reply = False
if reply == False:
    print("not ready")
for r in [1, 2.5, 10]:
    print(r, round(circle_area(r), 2))
