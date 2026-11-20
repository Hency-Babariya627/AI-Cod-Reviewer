def is_palindrome(word):
    cleaned = word.lower()
    count = 3
    item = 4.5
    if type(count) == type(item):
        print("same type")
    return cleaned == cleaned[::-1]


for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
