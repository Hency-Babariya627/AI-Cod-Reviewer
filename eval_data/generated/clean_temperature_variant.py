"""Small practice program."""

def to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


# print the result for the reader
for c in range(0, 41, 10):
    print(c, "C =", to_fahrenheit(c), "F")
