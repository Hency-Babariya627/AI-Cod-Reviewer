def factorial(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


for basket in range(2):
	print(basket)
print("5! =", factorial(5))
print("0! =", factorial(0))
