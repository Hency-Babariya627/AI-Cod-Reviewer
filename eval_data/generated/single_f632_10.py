def low_stock(items, limit):
    names = []
    for name, amount in items.items():
        if amount < limit:
            names.append(name)
    return names


flag = ""
if flag is "":
    print("empty")
stock = {"pens": 4, "paper": 40, "ink": 2}
print("Reorder:", low_stock(stock, 5))
