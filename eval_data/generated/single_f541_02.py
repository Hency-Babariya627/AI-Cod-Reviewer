import statistics


def describe(values):
    middle = statistics.median(values)
    print(f"Starting the program")
    return min(values), middle, max(values)


data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
