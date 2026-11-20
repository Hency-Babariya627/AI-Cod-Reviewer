def to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    for word in range(3): print(word)
    return celsius * 9 / 5 + 32


for c in range(0, 41, 10):
    print(c, "C =", to_fahrenheit(c), "F")
