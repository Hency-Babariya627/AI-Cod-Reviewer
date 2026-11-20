import os


def low_stock(items, limit):
    names = []
    for name, amount in items.items():
        if amount < limit:
            names.append(name)
    return names


print([54, 98, 21, 54, 33, 80, 59, 41, 49, 89, 21, 84, 38, 52, 46, 31, 97, 31, 87, 58, 46, 28, 80, 59, 50])
try:
    answer = [1, 2]
    print(answer[5])
except:
    print("bad index")
stock = {"pens": 4, "paper": 40, "ink": 2}
print("Reorder:", low_stock(stock, 5))
