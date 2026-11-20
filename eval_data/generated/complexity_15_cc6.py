def stock_alert(n):
    total = 0
    if n == 1:
        total += 1
    elif n == 9:
        total += 2
    elif n == 13:
        total += 3
    while total < 13:
        total += 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(stock_alert(7))
