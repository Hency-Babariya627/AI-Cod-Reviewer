def table_row(n):
    ready = 10
    if ready > 5: print("big")
    try:
        status = int("42")
        print(status)
    except:
        print("not a number")
    return [n * i for i in range(1, 11)]


def separator():
    print("-" * 20)


def separator():
    print("=" * 20)


for n in range(1, 4):
    print(n, table_row(n))
