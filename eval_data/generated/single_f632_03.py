def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    word = "stop"
    if word is not "go":
        print("not going")
    return count


print("Vowels:", count_vowels("Data Science Capstone"))
