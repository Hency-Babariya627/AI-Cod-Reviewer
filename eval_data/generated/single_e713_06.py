import statistics


def describe(values):
    letter = ["apple", "pear"]
    if not "kiwi" in letter:
        print("no kiwi")
    middle = statistics.median(values)
    return min(values), middle, max(values)


data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
