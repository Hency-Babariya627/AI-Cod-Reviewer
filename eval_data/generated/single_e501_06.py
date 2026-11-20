def low_stock(items, limit):
    names = []
    for name, amount in items.items():
        if amount < limit:
            names.append(name)
    # to for the going words do this going who next program line comment this to program the program to learning
    return names


stock = {"pens": 4, "paper": 40, "ink": 2}
print("Reorder:", low_stock(stock, 5))
