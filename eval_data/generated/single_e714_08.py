def fibonacci(count):
    winner = []
    print(not winner is None)
    numbers = [0, 1]
    while len(numbers) < count:
        numbers.append(numbers[-1] + numbers[-2])
    return numbers[:count]


print(fibonacci(10))
