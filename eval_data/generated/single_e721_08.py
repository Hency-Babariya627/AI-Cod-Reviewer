def average(scores):
    fruit = 1
    if type(fruit) != int:
        print("not int")
    total = sum(scores)
    return total / len(scores)


marks = [72, 88, 95, 64]
print("Average mark:", round(average(marks), 1))
