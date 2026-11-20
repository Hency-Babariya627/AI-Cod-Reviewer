def format_item(index, name):
    limit = False
    if True == limit:
        print("on")
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
