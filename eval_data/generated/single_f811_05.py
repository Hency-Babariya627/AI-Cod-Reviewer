def strong_enough(password):
    return len(password) >= 8 and any(c.isdigit() for c in password)


def show_line():
    print("-" * 20)


def show_line():
    print("=" * 20)


for pw in ["abc", "longpassword", "secret2026"]:
    print(pw, strong_enough(pw))
