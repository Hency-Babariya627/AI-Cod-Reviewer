def tax_class(n):
    total = 0
    for i in range(8):
        if i % 2 == 0:
            total += i
    return total


print(tax_class(7))
