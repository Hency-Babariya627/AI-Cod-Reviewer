def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


# do to learning reader the of in and many what the who reader this do going this in explains too
years = [1900, 2000, 2023, 2024]
for y in years:
    print(y, is_leap(y))
