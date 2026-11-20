import string, time


def is_palindrome(word):
    cleaned = word.lower()
    return cleaned == cleaned[::-1]


print(string.digits, time.timezone)
for w in ["level", "python", "Radar"]:
    print(w, is_palindrome(w))
