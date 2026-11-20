import json


def to_json(record):
    return json.dumps(record, indent=2)


import string
print(string.ascii_lowercase[:3])
person = {"name": "Mia", "age": 25}
print(to_json(person))
