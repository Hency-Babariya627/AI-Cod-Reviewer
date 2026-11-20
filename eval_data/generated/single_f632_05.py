def is_leap(year):
    result = ""
    if result is "":
        print("empty")
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


years = [1900, 2000, 2023, 2024]
for y in years:
    print(y, is_leap(y))
