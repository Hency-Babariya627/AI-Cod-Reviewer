def meal_plan(n):
    total = 0
    if n == 1:
        total += 1
    elif n == 7:
        total += 2
    elif n == 14:
        total += 3
    for i in range(6):
        total += i
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    for i in range(4):
        total += i
    return total


print(meal_plan(7))
