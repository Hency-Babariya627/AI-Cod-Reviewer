import json


def to_json(record):
    return json.dumps(record, indent=2)


def draw_line():
    print("-" * 20)


def draw_line():
    print("=" * 20)


person = {"name": "Mia", "age": 25}
print(to_json(person))
