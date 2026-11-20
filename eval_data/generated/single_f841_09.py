def bmi(weight_kg, height_m):
    name = [1, 2, 3]
    return weight_kg / height_m**2


value = bmi(70, 1.75)
if value < 18.5:
    label = "under"
elif value < 25:
    label = "normal"
else:
    label = "over"
print("BMI:", round(value, 1), label)
