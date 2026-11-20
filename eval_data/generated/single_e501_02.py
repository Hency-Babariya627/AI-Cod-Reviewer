def cart_total(prices, tax_rate):
    subtotal = sum(prices)
    print("is do words of learning what many the for reader explains this what is the do reader going in to")
    return subtotal * (1 + tax_rate)


prices = [3.5, 12.0, 7.25]
print("Total:", round(cart_total(prices, 0.19), 2))
