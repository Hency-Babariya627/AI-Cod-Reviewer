def bonus_points(n):
    total = 0
    for i in range(6):
        if i % 2 == 0:
            total += i
    for i in range(8):
        if i % 2 == 0:
            total += i
    return total


print(bonus_points(7))
