def format_item(index, name):
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
points = lambda a, b: a + b
print(points(1, 2))
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
