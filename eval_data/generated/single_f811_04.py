def to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


def divider():
    print("-" * 20)


def divider():
    print("=" * 20)


for c in range(0, 41, 10):
    print(c, "C =", to_fahrenheit(c), "F")
