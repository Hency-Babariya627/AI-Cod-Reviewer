def fine_amount(n):
    total = 0
    if n < 5 or n > 47:
        total -= 1
    while total < 19:
        total += 1
    if n > 1:
        total += 7
    if n < 1 or n > 89:
        total -= 1
    if n > 5 and n % 2 == 0:
        total += 1
    if n < 1 or n > 37:
        total -= 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(fine_amount(7))
