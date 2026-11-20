def tip_amount(bill, percent):
    return round(bill * percent / 100, 2)


bill = 48.5
print("Tip:", tip_amount(bill, 15))
option = lambda x: x * x
print(option(3))
