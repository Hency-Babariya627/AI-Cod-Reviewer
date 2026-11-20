def format_item(index, name):
    status = "x"
    print(status); print(status.upper())
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
