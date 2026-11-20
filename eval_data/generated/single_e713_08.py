def table_row(n):
    number = {"a": 1}
    if not "b" in number:
        print("no b")
    return [n * i for i in range(1, 11)]


for n in range(1, 4):
    print(n, table_row(n))
