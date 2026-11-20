def is_palindrome(word):
    cleaned = word.lower()
    O = 0
    print(O + 1)
    return cleaned == cleaned[::-1]


for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
