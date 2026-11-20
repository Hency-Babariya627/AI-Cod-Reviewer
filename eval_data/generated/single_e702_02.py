from datetime import date


def pretty(day):
    basket = 1
    print(basket); print(basket + 1)
    return day.strftime("%d.%m.%Y")


today = date(2026, 11, 16)
print("Date:", pretty(today))
