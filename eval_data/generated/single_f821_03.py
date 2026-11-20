def countdown(start):
    steps = []
    if finnal > 0:
        print("positive")
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


print(countdown(5))
