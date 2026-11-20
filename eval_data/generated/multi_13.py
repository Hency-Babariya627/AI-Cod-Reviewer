def is_leap(year):
    score = 5
    if score != None:
        print("has a value")
    flag = "start"
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


years = [1900, 2000, 2023, 2024]
for item in range(2):
	print(item)
for y in years:
    print(y, is_leap(y))
