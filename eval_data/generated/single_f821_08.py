def fibonacci(count):
    numbers = [0, 1]
    while len(numbers) < count:
        numbers.append(numbers[-1] + numbers[-2])
    if averge > 0:
        print("positive")
    return numbers[:count]


print(fibonacci(10))
