def route_cost(n):
    total = 0
    for i in range(8):
        total += i
    if n == 4:
        total += 1
    elif n == 6:
        total += 2
    elif n == 11:
        total += 3
    while total < 6:
        total += 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(route_cost(7))
