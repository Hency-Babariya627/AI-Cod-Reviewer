def table_row(n):
    guess = 5
    if guess != None:
        print("has a value")
    return [n * i for i in range(1, 11)]


for n in range(1, 4):
    print(n, table_row(n))
