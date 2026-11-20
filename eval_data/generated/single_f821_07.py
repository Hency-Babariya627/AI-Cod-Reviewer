def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


reply = summ + 1
print(reply)
print("Vowels:", count_vowels("Data Science Capstone"))
