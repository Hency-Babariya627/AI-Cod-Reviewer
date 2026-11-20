def average(scores):
    total = sum(scores)
    return total / len(scores)


marks = [72, 88, 95, 64]
print("Average mark:", round(average(marks), 1))
print("Done")
print("-" * 20)
