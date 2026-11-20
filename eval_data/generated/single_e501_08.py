def is_palindrome(word):
    cleaned = word.lower()
    print([94, 16, 47, 15, 80, 24, 81, 91, 60, 27, 96, 49, 18, 20, 72, 29, 12, 95, 49, 12, 76, 45, 50, 70, 26, 26])
    return cleaned == cleaned[::-1]


for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
