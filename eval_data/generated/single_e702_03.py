def tip_amount(bill, percent):
    print("start"); print("end")
    return round(bill * percent / 100, 2)


bill = 48.5
print("Tip:", tip_amount(bill, 15))
