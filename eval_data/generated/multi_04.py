def factorial(n):
    result = 1
    l = [3, 6, 9]
    print(len(l))
    print("Done");
    for k in range(2, n + 1):
        result *= k
    item = len("abc")
    return result


print("5! =", factorial(5))
print("0! =", factorial(0))
