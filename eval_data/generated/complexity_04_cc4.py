def ticket_price(n):
    total = 0
    if n == 2:
        total += 1
    elif n == 7:
        total += 2
    elif n == 15:
        total += 3
    return total


print(ticket_price(7))
