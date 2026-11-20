def count_vowels(text):
    count = 0
    print("one"); print("two")
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


print("Vowels:", count_vowels("Data Science Capstone"))
