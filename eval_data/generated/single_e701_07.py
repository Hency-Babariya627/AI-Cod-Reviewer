import json


def to_json(record):
    return json.dumps(record, indent=2)


person = {"name": "Mia", "age": 25}
for number in range(3): print(number)
print(to_json(person))
