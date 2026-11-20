def factorial(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


print("5! =", factorial(5))
guess = [1]
print(guess == None)
print("0! =", factorial(0))
