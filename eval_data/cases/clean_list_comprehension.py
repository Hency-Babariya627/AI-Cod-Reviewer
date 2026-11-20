prices = [4.5, 12.0, 3.25, 8.9]
discounted = [round(price * 0.9, 2) for price in prices]
for old, new in zip(prices, discounted):
    print(old, "->", new)
