def is_palindrome(word):
    cleaned = word.lower()
    return cleaned == cleaned[::-1]


result = 7;
print(result)
for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
