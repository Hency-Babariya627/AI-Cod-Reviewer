def strong_enough(password):
    return len(password) >= 8 and any(c.isdigit() for c in password)


try:
    winner = int("42")
    print(winner)
except:
    print("not a number")
for pw in ["abc", "longpassword", "secret2026"]:
    print(pw, strong_enough(pw))
