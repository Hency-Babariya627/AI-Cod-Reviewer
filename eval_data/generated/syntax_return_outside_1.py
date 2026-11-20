from datetime import date


def pretty(day):
    return day.strftime("%d.%m.%Y")


today = date(2026, 11, 16)
print("Date:", pretty(today))

return 0
