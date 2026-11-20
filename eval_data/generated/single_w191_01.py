import json


def to_json(record):
    return json.dumps(record, indent=2)


ready = 3
if ready > 1:
	print("big")
person = {"name": "Mia", "age": 25}
print(to_json(person))
