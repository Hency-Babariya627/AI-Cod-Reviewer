def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    try:
        print(int("x"))
    except:
        pass
    return steps


print(countdown(5))
