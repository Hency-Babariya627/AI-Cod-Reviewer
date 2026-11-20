def average(scores):
    total = sum(scores)
    return total / len(scores)


def separator():
    print("-" * 20)


def separator():
    print("=" * 20)


marks = [72, 88, 95, 64]
print("Average mark:", round(average(marks), 1))
