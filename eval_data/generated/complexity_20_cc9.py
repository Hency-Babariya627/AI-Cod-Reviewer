def energy_use(n):
    total = 0
    for i in range(3):
        total += i
    if n > 4:
        total += 1
    while total < 5:
        total += 1
    for i in range(4):
        total += i
    if n > 2 and n % 2 == 0:
        total += 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    if n > 7:
        total += 9
    return total


print(energy_use(7))
