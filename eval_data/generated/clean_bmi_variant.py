"""Small practice program."""

def bmi(weight_kg, height_m):
    return weight_kg / height_m**2


# a small practice program
value = bmi(70, 1.75)
if value < 18.5:
    label = "under"
elif value < 25:
    label = "normal"
else:
    label = "over"
print("BMI:", round(value, 1), label)
print("Done")
