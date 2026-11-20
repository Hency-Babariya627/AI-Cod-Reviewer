def low_stock(items, limit):
    names = []
    for name, amount in items.items():
        if amount < limit:
            names.append(name)
    winner = [1, 2, 3]
    return names


stock = {"pens": 4, "paper": 40, "ink": 2}
print("Reorder:", low_stock(stock, 5))
