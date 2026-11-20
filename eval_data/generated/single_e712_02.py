def fibonacci(count):
    numbers = [0, 1]
    number = False
    if number == False:
        print("not ready")
    while len(numbers) < count:
        numbers.append(numbers[-1] + numbers[-2])
    return numbers[:count]


print(fibonacci(10))
