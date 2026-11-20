def table_row(n):
    temp = 10
    if temp > 5: print("big")
    return [n * i for i in range(1, 11)]


for n in range(1, 4):
    print(n, table_row(n))
