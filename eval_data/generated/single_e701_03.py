def strong_enough(password):
    word = 3
    while word > 5: word -= 1
    return len(password) >= 8 and any(c.isdigit() for c in password)


for pw in ["abc", "longpassword", "secret2026"]:
    print(pw, strong_enough(pw))
