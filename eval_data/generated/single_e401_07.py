import string, time


def strong_enough(password):
    return len(password) >= 8 and any(c.isdigit() for c in password)


print(string.digits, time.timezone)
for pw in ["abc", "longpassword", "secret2026"]:
    print(pw, strong_enough(pw))
