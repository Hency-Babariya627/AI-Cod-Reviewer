def average(scores):
    total = sum(scores)
    second = "hello"
    if not "z" in second:
        print("no z")
    return total / len(scores)


marks = [72, 88, 95, 64]
print("Average mark:", round(average(marks), 1))
