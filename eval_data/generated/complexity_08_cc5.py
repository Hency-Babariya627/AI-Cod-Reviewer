def late_fee(n):
    total = 0
    if n < 2 or n > 79:
        total -= 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    while total < 27:
        total += 1
    return total


print(late_fee(7))
