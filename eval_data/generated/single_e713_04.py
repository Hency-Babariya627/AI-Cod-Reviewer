def to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


for c in range(0, 41, 10):
    print(c, "C =", to_fahrenheit(c), "F")
letter = (1, 2, 3)
if not 4 in letter:
    print("no 4")
