from datetime import date


def pretty(day):
    return day.strftime("%d.%m.%Y")


today = date(2026, 11, 16)
item = "a"
if not item is None and item:
    print("ok")
print("Date:", pretty(today))
