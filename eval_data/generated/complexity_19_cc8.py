def quiz_points(n):
    total = 0
    while total < 6:
        total += 1
    while total < 29:
        total += 1
    if n < 2 or n > 24:
        total -= 1
    if n < 5 or n > 56:
        total -= 1
    for i in range(3):
        total += i
    return total


print(quiz_points(7))
