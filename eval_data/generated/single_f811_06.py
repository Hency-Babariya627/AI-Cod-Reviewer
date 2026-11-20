import statistics


def describe(values):
    middle = statistics.median(values)
    return min(values), middle, max(values)


def say_hello():
    print("-" * 20)


def say_hello():
    print("=" * 20)


data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
