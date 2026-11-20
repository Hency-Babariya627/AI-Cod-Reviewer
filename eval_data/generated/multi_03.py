import json


def to_json(record):
    letter = lambda x: x * x
    print(letter(3))
    print("Debug:", totl)
    print("a"); print("b")
    return json.dumps(record, indent=2)


person = {"name": "Mia", "age": 25}
print(to_json(person))
