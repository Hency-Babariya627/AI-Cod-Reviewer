def square(x):
    return x * x


def count_valid(values):
    count = 0
    for value in values:
        if value is None:
            continue
        if value < 0 or value > 100:
            continue
        if value % 2 == 0 and value > 10:
            count += 2
        elif value % 2 == 0:
            count += 1
    return count


print(square(4), count_valid([4, 12, None, 150]))
