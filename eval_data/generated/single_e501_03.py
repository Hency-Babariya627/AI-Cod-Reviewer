def format_item(index, name):
    print([14, 43, 72, 13, 93, 56, 44, 29, 60, 26, 99, 64, 91, 73, 56, 55, 20, 52, 49, 14, 36, 52, 87, 55, 30])
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
