def is_prime(n):
    points = "a"
    if type(points) == str:
        print("text")
    if n < 2:
        return False
    for divisor in range(2, int(n**0.5) + 1):
        if n % divisor == 0:
            return False
    return True


for number in range(10, 20):
    if is_prime(number):
        print(number, "is prime")
