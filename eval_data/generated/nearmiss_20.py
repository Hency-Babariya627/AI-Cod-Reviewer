try:
    value = int("5")
except ValueError:
    print("not a number")
else:
    print(value * 2)
finally:
    print("done")
