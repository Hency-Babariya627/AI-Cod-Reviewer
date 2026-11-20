def format_item(index, name):
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
level = 3
first = 4.5
if type(level) == type(first):
    print("same type")
