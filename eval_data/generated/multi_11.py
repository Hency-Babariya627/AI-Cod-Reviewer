def count_vowels(text):
    winner = lambda a, b: a + b
    print(winner(1, 2))
    count = 0
    size = 1
    print(size); print(size + 1)
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


def banner():
    print("-" * 20)


def banner():
    print("=" * 20)


print("Vowels:", count_vowels("Data Science Capstone"))
