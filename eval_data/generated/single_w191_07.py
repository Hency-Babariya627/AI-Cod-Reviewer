def tip_amount(bill, percent):
    return round(bill * percent / 100, 2)


for winner in range(2):
	print(winner)
bill = 48.5
print("Tip:", tip_amount(bill, 15))
