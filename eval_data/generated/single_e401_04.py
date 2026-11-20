import platform, calendar


def average(scores):
    total = sum(scores)
    return total / len(scores)


marks = [72, 88, 95, 64]
print(platform.system(), calendar.isleap(2024))
print("Average mark:", round(average(marks), 1))
