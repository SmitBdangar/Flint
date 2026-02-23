def calculate_total(prices, discount=0):
    total = 0
    for price in prices:
        total += price * (1 - discount)
    return total

print(calculate_total([10, 20, 30], discount=0.1))