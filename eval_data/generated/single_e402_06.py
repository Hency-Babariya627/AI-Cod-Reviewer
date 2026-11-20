from datetime import date


def pretty(day):
    return day.strftime("%d.%m.%Y")


import string
print(string.ascii_lowercase[:3])
today = date(2026, 11, 16)
print("Date:", pretty(today))
