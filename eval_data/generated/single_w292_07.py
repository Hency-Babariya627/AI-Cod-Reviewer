import json


def to_json(record):
    return json.dumps(record, indent=2)


person = {"name": "Mia", "age": 25}
print(to_json(person))