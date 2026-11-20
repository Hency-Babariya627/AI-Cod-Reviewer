def check_password(password):
    problems = 0
    if len(password) < 8:
        problems += 1
    if password.lower() == password:
        problems += 1
    if password.upper() == password:
        problems += 1
    has_digit = False
    for char in password:
        if char.isdigit():
            has_digit = True
    if not has_digit:
        problems += 1
    if " " in password or "\t" in password:
        problems += 1
    for bad in ["1234", "password", "qwerty"]:
        if bad in password.lower():
            problems += 1
    return problems == 0


print(check_password("Summer2026"))
