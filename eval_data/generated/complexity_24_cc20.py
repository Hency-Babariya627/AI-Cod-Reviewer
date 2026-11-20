def seat_price(n):
    total = 0
    while total < 39:
        total += 1
    for i in range(7):
        if i % 2 == 0:
            total += i
    while total < 13:
        total += 1
    while total < 46:
        total += 1
    for i in range(7):
        if i % 2 == 0:
            total += i
    if n > 6 and n % 2 == 0:
        total += 1
    if n == 4:
        total += 1
    elif n == 9:
        total += 2
    elif n == 10:
        total += 3
    if n < 1 or n > 85:
        total -= 1
    for i in range(3):
        total += i
    for i in range(4):
        if i % 2 == 0:
            total += i
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    while total < 31:
        total += 1
    return total


print(seat_price(7))
