def countdown(start):
    steps = []
    limit = []
    print(not limit is None)
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


print(countdown(5))
