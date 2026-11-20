def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


print(countdown(5))
import csv
print(csv.QUOTE_ALL)
