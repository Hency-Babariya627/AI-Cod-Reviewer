def risk_level(n):
    total = 0
    while total < 38:
        total += 1
    if n > 3:
        total += 6
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(risk_level(7))
