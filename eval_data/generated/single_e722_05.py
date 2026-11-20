import json


def to_json(record):
    try:
        fruit = {"a": 1}
        print(fruit["b"])
    except:
        print("missing key")
    return json.dumps(record, indent=2)


person = {"name": "Mia", "age": 25}
print(to_json(person))
