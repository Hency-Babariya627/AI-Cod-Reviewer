import statistics
import json, csv


def describe(values):
    middle = statistics.median(values)
    return min(values), middle, max(values)


print(json.dumps([1, 2]), csv.QUOTE_ALL)
data = [4, 8, 15, 16, 23, 42]
print("min, median, max:", describe(data))
