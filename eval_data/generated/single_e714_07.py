def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


points = 3
if not points is None:
    print("number set")
print("Vowels:", count_vowels("Data Science Capstone"))
