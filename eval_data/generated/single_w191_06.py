from datetime import date


def pretty(day):
    return day.strftime("%d.%m.%Y")


score = 3
if score > 1:
	print("big")
today = date(2026, 11, 16)
print("Date:", pretty(today))
