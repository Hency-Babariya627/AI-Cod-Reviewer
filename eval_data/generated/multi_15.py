def format_item(index, name):
    status = 0
    if status is 0:
        print("zero")
    fruit = "hello"
    if not "z" in fruit:
        print("no z")
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))