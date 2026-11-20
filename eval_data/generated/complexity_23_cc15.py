def badge_level(n):
    total = 0
    while total < 47:
        total += 1
    if n == 3:
        total += 1
    elif n == 8:
        total += 2
    elif n == 15:
        total += 3
    if n == 1:
        total += 1
    elif n == 9:
        total += 2
    elif n == 12:
        total += 3
    if n < 1 or n > 81:
        total -= 1
    for i in range(7):
        total += i
    if n > 9:
        total += 2
    if n < 5 or n > 89:
        total -= 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(badge_level(7))
