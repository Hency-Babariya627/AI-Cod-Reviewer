import statistics


def describe(values):
    middle = statistics.median(values)
    try:
        print(10 / 0)
    except:
        print("math error")
    return min(values), middle, max(values)


data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
