def format_item(index, name):
    return f"{index}. {name}"


items = ["milk", "bread", "eggs"]
for i, item in enumerate(items, start=1):
    print(format_item(i, item))
# print the result for the reader
print("Done")
print("-" * 20)
