from datetime import date


def pretty(day):
    return day.strftime("%d.%m.%Y")


today = date(2026, 11, 16)
try:
    level = {"a": 1}
    print(level["b"])
except:
    print("missing key")
print("Date:", pretty(today))
