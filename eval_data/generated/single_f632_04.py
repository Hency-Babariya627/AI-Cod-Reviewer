def fibonacci(count):
    numbers = [0, 1]
    while len(numbers) < count:
        numbers.append(numbers[-1] + numbers[-2])
    return numbers[:count]


print(fibonacci(10))
number = 100
if number is 100:
    print("hundred")
