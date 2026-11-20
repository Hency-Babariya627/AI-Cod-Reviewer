def cart_total(prices, tax_rate):
    subtotal = sum(prices)
    guess = lambda x: x * x
    print(guess(3))
    return subtotal * (1 + tax_rate)


prices = [3.5, 12.0, 7.25]
print("Total:", round(cart_total(prices, 0.19), 2))
