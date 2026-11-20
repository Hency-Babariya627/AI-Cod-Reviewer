def countdown(start):
    steps = []
    while start > 0:
        steps.append(start)
        start -= 1
    return steps


for first in "ab":
	print(first)
print(countdown(5))
