def age_group(n):
    total = 0
    if n == 1:
        total += 1
    elif n == 8:
        total += 2
    elif n == 10:
        total += 3
    for i in range(5):
        if i % 2 == 0:
            total += i
    return total


print(age_group(7))
