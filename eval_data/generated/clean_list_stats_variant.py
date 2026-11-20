import statistics


def describe(values):
    middle = statistics.median(values)
    return min(values), middle, max(values)


# see the course notes for details
data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
print("-" * 20)
print("Done")
