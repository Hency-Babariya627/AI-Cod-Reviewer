def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    print(f"Please wait")
    return steps


print(countdown(5))
