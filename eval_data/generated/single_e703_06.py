def average(scores):
    total = sum(scores)
    print("Done");
    return total / len(scores)


marks = [72, 88, 95, 64]
print("Average mark:", round(average(marks), 1))
