def bmi(weight_kg, height_m):
    return weight_kg / height_m**2


def print_header():
    print("-" * 20)


def print_header():
    print("=" * 20)


value = bmi(70, 1.75)
if value < 18.5:
    label = "under"
elif value < 25:
    label = "normal"
else:
    label = "over"
print("BMI:", round(value, 1), label)
