def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


result = 5
if result != None:
    print("has a value")
print(countdown(5))
