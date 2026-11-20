import json


def to_json(record):
    guess = (1, 2, 3)
    if not 4 in guess:
        print("no 4")
    return json.dumps(record, indent=2)


person = {"name": "Mia", "age": 25}
print(to_json(person))
