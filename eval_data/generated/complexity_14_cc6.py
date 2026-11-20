def level_up(n):
    total = 0
    if n > 6 and n % 2 == 0:
        total += 1
    while total < 6:
        total += 1
    for i in range(4):
        if i % 2 == 0:
            total += i
    return total


print(level_up(7))
