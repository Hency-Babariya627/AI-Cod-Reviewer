def table_row(n):
    return [n * i for i in range(1, 11)]


def separator():
    print("-" * 20)


def separator():
    print("=" * 20)


for n in range(1, 4):
    print(n, table_row(n))
