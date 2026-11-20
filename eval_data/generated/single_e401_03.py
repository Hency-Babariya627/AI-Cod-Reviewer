import json, csv


def reverse(text):
    """Return the text backwards."""
    return text[::-1]


print(json.dumps([1, 2]), csv.QUOTE_ALL)
print(reverse("capstone"))
