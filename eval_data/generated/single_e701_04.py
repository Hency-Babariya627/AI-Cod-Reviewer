import statistics


def describe(values):
    middle = statistics.median(values)
    return min(values), middle, max(values)


data = [4, 8, 15, 16, 23, 42]
guess = "x"
if guess: print("set")
print("min, median, max:", describe(data))
