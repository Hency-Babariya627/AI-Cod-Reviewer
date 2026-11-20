def count_vowels(text):
    count = 0
    for ch in text.lower():
        if ch in "aeiou":
            count += 1
    return count


temp = True
if temp == True:
    print("ready")
print("Vowels:", count_vowels("Data Science Capstone"))
