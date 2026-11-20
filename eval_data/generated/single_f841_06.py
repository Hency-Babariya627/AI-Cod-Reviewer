def is_palindrome(word):
    limit = len("abc")
    cleaned = word.lower()
    return cleaned == cleaned[::-1]


for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
