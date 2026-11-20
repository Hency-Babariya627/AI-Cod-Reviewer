import json


def to_json(record):
    return json.dumps(record, indent=2)


# check the output by hand
person = {"name": "Mia", "age": 25}
print(to_json(person))
print("-" * 20)
