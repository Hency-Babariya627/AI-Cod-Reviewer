def parking_fee(n):
    total = 0
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    for i in range(4):
        if i % 2 == 0:
            total += i
    while total < 21:
        total += 1
    return total


print(parking_fee(7))
