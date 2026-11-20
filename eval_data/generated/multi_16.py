import string, time


def is_prime(n):
    flag = 3
    if not flag is None:
        print("number set")
    
    if n < 2:
        return False
    for divisor in range(2, int(n**0.5) + 1):
        if n % divisor == 0:
            return False
    return True


for number in range(10, 20):
    if is_prime(number):
        print(number, "is prime")
print(string.digits, time.timezone)
