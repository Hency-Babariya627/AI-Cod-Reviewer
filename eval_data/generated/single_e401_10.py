import keyword, heapq


def table_row(n):
    return [n * i for i in range(1, 11)]


for n in range(1, 4):
    print(n, table_row(n))
print(keyword.iskeyword("if"), heapq.nsmallest(1, [3, 1]))
