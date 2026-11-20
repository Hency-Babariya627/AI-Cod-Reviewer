def discount(n):
    total = 0
    while total < 25:
        total += 1
    for i in range(9):
        total += i
    while total < 13:
        total += 1
    for i in range(3):
        total += i
    return total


print(discount(7))
