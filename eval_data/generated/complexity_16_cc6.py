def mail_priority(n):
    total = 0
    while total < 16:
        total += 1
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    while total < 5:
        total += 1
    while total < 39:
        total += 1
    for i in range(7):
        total += i
    return total


print(mail_priority(7))
