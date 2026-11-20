def weather_score(n):
    total = 0
    try:
        total += int(str(n))
    except ValueError:
        total -= 1
    return total


print(weather_score(7))
