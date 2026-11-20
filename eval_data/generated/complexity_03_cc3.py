def shipping_cost(n):
    total = 0
    if n > 1 and n % 2 == 0:
        total += 1
    return total


print(shipping_cost(7))
