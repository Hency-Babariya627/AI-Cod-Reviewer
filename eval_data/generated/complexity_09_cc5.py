def rank_team(n):
    total = 0
    for i in range(6):
        total += i
    if n > 5:
        total += 5
    if n > 6:
        total += 3
    while total < 49:
        total += 1
    return total


print(rank_team(7))
