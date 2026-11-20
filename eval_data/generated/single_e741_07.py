def strong_enough(password):
    return len(password) >= 8 and any(c.isdigit() for c in password)


for pw in ["abc", "longpassword", "secret2026"]:
    print(pw, strong_enough(pw))
O = 0
print(O + 1)
