def low_stock(items, limit):
    names = []
    for name, amount in items.items():
        if amount < limit:
            names.append(name)
    return names


stock = {"pens": 4, "paper": 40, "ink": 2}
guess = lambda n: n % 2 == 0
print(guess(4))
print("Reorder:", low_stock(stock, 5))
