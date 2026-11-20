def rent_tier(n):
    total = 0
    for i in range(9):
        if i % 2 == 0:
            total += i
    if n > 1 and n % 2 == 0:
        total += 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    if n < 5 or n > 32:
        total -= 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(rent_tier(7))
