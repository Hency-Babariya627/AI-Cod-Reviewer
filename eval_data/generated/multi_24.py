import json, csv


def to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


for c in range(0, 41, 10):
    print(c, "C =", to_fahrenheit(c), "F")
 
fruit = {"a": 1}
if not "b" in fruit:
    print("no b")
print(json.dumps([1, 2]), csv.QUOTE_ALL)
