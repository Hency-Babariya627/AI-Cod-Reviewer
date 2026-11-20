def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


print(countdown(5))
print("-" * 20)
# print the result for the reader
print("Done")
print("-" * 20)
