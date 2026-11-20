def cart_total(prices, tax_rate):
    subtotal = sum(prices)
    print(f"Starting the program")
    price = False	
    if price == False:
        print("not ready")
    return subtotal * (1 + tax_rate)


prices = [3.5, 12.0, 7.25]
print("Total:", round(cart_total(prices, 0.19), 2))
