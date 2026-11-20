#!/usr/bin/env python3
"""Generate the balanced evaluation set for the AI Code Reviewer.

Design: every case is built from a small, clean beginner program ("base") by applying
a documented edit. The expected findings come from the edit itself (known by
construction), never from the output of the tool being evaluated. Ruff, compile() and a
complexity counter are run afterwards only to catch design mistakes (see verify()).

Run:  python generate_dataset.py <output_folder>
Reproducible: fixed random seed.
"""
import ast
import json
import warnings
import random
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

warnings.simplefilter("ignore")  # the generated files contain deliberate mistakes
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("generated")
SEED = 2026
FLAG_AT = 6  # Radon rank B starts at 6

# ---------------------------------------------------------------- building blocks
class S:
    """One statement (possibly several lines) of a program."""
    n = 0

    def __init__(self, t):
        S.n += 1
        self.id = S.n
        self.t = t


def mk(imports, fdef, fbody, main, cls=None):
    return {
        "imports": [S(x) for x in imports], "fdef": fdef, "fbody": [S(x) for x in fbody],
        "between": [], "cls": ({"head": cls[0], "mbody": [S(x) for x in cls[1]]} if cls else None),
        "main": [S(x) for x in main], "eof_nl": True, "modedoc": None,
    }


def compose(p):
    lines, pos = [], {}

    def put(s):
        pos[s.id] = len(lines) + 1
        lines.extend(s.t.split("\n"))

    if p["modedoc"]:
        lines += [p["modedoc"], ""]
    for s in p["imports"]:
        put(s)
    if p["imports"]:
        lines += ["", ""]
    lines.append(p["fdef"])
    for s in p["fbody"]:
        put(s)
    lines += ["", ""]
    for s in p["between"]:
        put(s)
        lines += ["", ""]
    if p["cls"]:
        lines.extend(p["cls"]["head"])
        for s in p["cls"]["mbody"]:
            put(s)
        lines += ["", ""]
    for s in p["main"]:
        put(s)
    return "\n".join(lines) + ("\n" if p["eof_nl"] else ""), pos


def clone(p):
    q = dict(p)
    q["imports"] = [S(s.t) for s in p["imports"]]
    q["fbody"] = [S(s.t) for s in p["fbody"]]
    q["between"] = [S(s.t) for s in p["between"]]
    q["main"] = [S(s.t) for s in p["main"]]
    q["cls"] = ({"head": p["cls"]["head"], "mbody": [S(s.t) for s in p["cls"]["mbody"]]}
                if p["cls"] else None)
    return q


# 25 clean beginner programs (themes differ; some have imports, some a class)
BASES = {}


def base(name, imports, fdef, fbody, main, cls=None):
    BASES[name] = mk(imports, fdef, fbody, main, cls)


base("temperature", [], "def to_fahrenheit(celsius):",
     ['    """Convert Celsius to Fahrenheit."""', "    return celsius * 9 / 5 + 32"],
     ['for c in range(0, 41, 10):\n    print(c, "C =", to_fahrenheit(c), "F")'])
base("grade_average", [], "def average(scores):",
     ["    total = sum(scores)", "    return total / len(scores)"],
     ["marks = [72, 88, 95, 64]", 'print("Average mark:", round(average(marks), 1))'])
base("cart_total", [], "def cart_total(prices, tax_rate):",
     ["    subtotal = sum(prices)", "    return subtotal * (1 + tax_rate)"],
     ["prices = [3.5, 12.0, 7.25]", 'print("Total:", round(cart_total(prices, 0.19), 2))'])
base("word_count", [], "def count_words(text):",
     ["    words = text.split()", "    return len(words)"],
     ['sentence = "the quick brown fox jumps"', 'print("Words:", count_words(sentence))'])
base("palindrome", [], "def is_palindrome(word):",
     ["    cleaned = word.lower()", "    return cleaned == cleaned[::-1]"],
     ['for w in ["level", "python", "Radar"]:\n    print(w, is_palindrome(w))'])
base("prime_check", [], "def is_prime(n):",
     ["    if n < 2:\n        return False",
      "    for divisor in range(2, int(n**0.5) + 1):\n        if n % divisor == 0:\n            return False",
      "    return True"],
     ["for number in range(10, 20):\n    if is_prime(number):\n        print(number, \"is prime\")"])
base("leap_year", [], "def is_leap(year):",
     ["    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)"],
     ["years = [1900, 2000, 2023, 2024]", 'for y in years:\n    print(y, is_leap(y))'])
base("factorial", [], "def factorial(n):",
     ["    result = 1", "    for k in range(2, n + 1):\n        result *= k", "    return result"],
     ['print("5! =", factorial(5))', 'print("0! =", factorial(0))'])
base("fibonacci", [], "def fibonacci(count):",
     ["    numbers = [0, 1]",
      "    while len(numbers) < count:\n        numbers.append(numbers[-1] + numbers[-2])",
      "    return numbers[:count]"],
     ['print(fibonacci(10))'])
base("bmi", [], "def bmi(weight_kg, height_m):",
     ["    return weight_kg / height_m**2"],
     ["value = bmi(70, 1.75)",
      'if value < 18.5:\n    label = "under"\nelif value < 25:\n    label = "normal"\nelse:\n    label = "over"',
      'print("BMI:", round(value, 1), label)'])
base("tip", [], "def tip_amount(bill, percent):",
     ["    return round(bill * percent / 100, 2)"],
     ["bill = 48.5", 'print("Tip:", tip_amount(bill, 15))'])
base("reverse_string", [], "def reverse(text):",
     ['    """Return the text backwards."""', "    return text[::-1]"],
     ['print(reverse("capstone"))'])
base("vowels", [], "def count_vowels(text):",
     ["    count = 0",
      '    for ch in text.lower():\n        if ch in "aeiou":\n            count += 1',
      "    return count"],
     ['print("Vowels:", count_vowels("Data Science Capstone"))'])
base("times_table", [], "def table_row(n):",
     ["    return [n * i for i in range(1, 11)]"],
     ["for n in range(1, 4):\n    print(n, table_row(n))"])
base("list_stats", ["import statistics"], "def describe(values):",
     ["    middle = statistics.median(values)", "    return min(values), middle, max(values)"],
     ["data = [4, 8, 15, 16, 23, 42]", 'print("min, median, max:", describe(data))'])
base("random_pick", ["import random"], "def pick(options):",
     ["    return random.choice(options)"],
     ["random.seed(3)", 'print("Today:", pick(["tea", "coffee", "water"]))'])
base("date_format", ["from datetime import date"], "def pretty(day):",
     ['    return day.strftime("%d.%m.%Y")'],
     ["today = date(2026, 11, 16)", 'print("Date:", pretty(today))'])
base("json_dump", ["import json"], "def to_json(record):",
     ["    return json.dumps(record, indent=2)"],
     ['person = {"name": "Mia", "age": 25}', "print(to_json(person))"])
base("circle_area", ["import math"], "def circle_area(radius):",
     ["    return math.pi * radius**2"],
     ["for r in [1, 2.5, 10]:\n    print(r, round(circle_area(r), 2))"])
base("inventory", [], "def low_stock(items, limit):",
     ["    names = []", "    for name, amount in items.items():\n        if amount < limit:\n            names.append(name)",
      "    return names"],
     ['stock = {"pens": 4, "paper": 40, "ink": 2}', 'print("Reorder:", low_stock(stock, 5))'])
base("title_case", [], "def title_case(text):",
     ['    return " ".join(word.capitalize() for word in text.split())'],
     ['print(title_case("learning python is fun"))'])
base("password", [], "def strong_enough(password):",
     ["    return len(password) >= 8 and any(c.isdigit() for c in password)"],
     ['for pw in ["abc", "longpassword", "secret2026"]:\n    print(pw, strong_enough(pw))'])
base("shopping_list", [], "def format_item(index, name):",
     ['    return f"{index}. {name}"'],
     ['items = ["milk", "bread", "eggs"]', 'for i, item in enumerate(items, start=1):\n    print(format_item(i, item))'])
base("countdown", [], "def countdown(start):",
     ["    steps = []", "    while start > 0:\n        steps.append(start)\n        start -= 1",
      "    return steps"],
     ['print(countdown(5))'])
base("account_class", [], "def format_money(amount):",
     ['    return f"{amount:.2f} EUR"'],
     ['account = Account("Ada")', "account.deposit(50)", 'print(account.describe())'],
     cls=(["class Account:", "    def __init__(self, owner):", "        self.owner = owner",
           "        self.balance = 0", "", "    def deposit(self, amount):",
           "        self.balance += amount", "", "    def describe(self):"],
          ['        return f"{self.owner} has {format_money(self.balance)}"']))
base("counter_class", [], "def percent(part, whole):",
     ["    return round(part / whole * 100, 1)"],
     ['tally = Tally()', 'tally.add("a")', 'tally.add("a")', 'tally.add("b")',
      'print("a share:", percent(tally.counts["a"], tally.total()), "%")'],
     cls=(["class Tally:", "    def __init__(self):", "        self.counts = {}", "",
           "    def add(self, key):", "        self.counts[key] = self.counts.get(key, 0) + 1", "",
           "    def total(self):"],
          ["        return sum(self.counts.values())"]))
BASE_NAMES = list(BASES)

# ---------------------------------------------------------------- name pools
VARS = ["count", "name", "score", "level", "item", "price", "status", "result", "number",
        "answer", "choice", "reply", "option", "limit", "flag", "ready", "winner", "basket",
        "fruit", "first", "second", "word", "letter", "temp", "points", "guess", "size"]
TYPOS = ["totl", "reslt", "countt", "nmae", "scor", "averge", "summ", "ammount", "pricee",
         "lenght", "finnal", "resutl", "valeu", "numbr"]
FILLER = ("this comment explains in far too many words what the next line of the program is "
          "going to do for the reader who is learning python and wants to understand it").split()
WORDS = ("table river garden window yellow silver market button planet orange bridge forest "
         "letter pocket ticket morning winter coffee shadow marble anchor").split()


def has_word(text, w):
    return re.search(r"\b" + re.escape(w) + r"\b", text) is not None


def pick_names(rng, text, pool, k):
    cand = [w for w in pool if not has_word(text, w)]
    rng.shuffle(cand)
    if len(cand) < k:
        raise RuntimeError("name pool exhausted")
    return cand[:k]


# ---------------------------------------------------------------- templates
# '⟦RULE⟧' at the start of a line marks the line the rule must be reported on.
MARK = re.compile(r"^⟦([A-Z]\d{3})⟧")
T = {}
T["F541"] = [['⟦F541⟧print(f"Done")'], ['⟦F541⟧print(f"Starting the program")'],
             ['⟦F541⟧print(f"----------")'], ['⟦F541⟧print(f"Please wait")'],
             ['⟦F541⟧print(f"All steps finished")']]
T["F821"] = [['⟦F821⟧print("Debug:", <<t1>>)'], ['⟦F821⟧<<n1>> = <<t1>> + 1', "print(<<n1>>)"],
             ["⟦F821⟧if <<t1>> > 0:", '    print("positive")'], ["⟦F821⟧print(len(<<t1>>))"],
             ["⟦F821⟧print(<<t1>>.upper())"]]
T["F841"] = [['⟦F841⟧<<n1>> = len("abc")'], ['⟦F841⟧<<n1>> = "start"'], ["⟦F841⟧<<n1>> = 0"],
             ["⟦F841⟧<<n1>> = [1, 2, 3]"], ['⟦F841⟧<<n1>> = input("Press enter")']]
T["F632"] = [['<<n1>> = "yes"', '⟦F632⟧if <<n1>> is "yes":', '    print("agreed")'],
             ["<<n1>> = 0", "⟦F632⟧if <<n1>> is 0:", '    print("zero")'],
             ['<<n1>> = "stop"', '⟦F632⟧if <<n1>> is not "go":', '    print("not going")'],
             ["<<n1>> = 100", "⟦F632⟧if <<n1>> is 100:", '    print("hundred")'],
             ['<<n1>> = ""', '⟦F632⟧if <<n1>> is "":', '    print("empty")']]
T["E701"] = [["<<n1>> = 10", '⟦E701⟧if <<n1>> > 5: print("big")'],
             ["⟦E701⟧for <<n1>> in range(3): print(<<n1>>)"],
             ["<<n1>> = 3", "⟦E701⟧while <<n1>> > 5: <<n1>> -= 1"],
             ['<<n1>> = "x"', '⟦E701⟧if <<n1>>: print("set")'], ["⟦E701⟧class <<N1>>: pass"]]
T["E702"] = [['⟦E702⟧print("a"); print("b")'], ["<<n1>> = 1", "⟦E702⟧print(<<n1>>); print(<<n1>> + 1)"],
             ['⟦E702⟧print("start"); print("end")'], ['<<n1>> = "x"', "⟦E702⟧print(<<n1>>); print(<<n1>>.upper())"],
             ['⟦E702⟧print("one"); print("two")']]
T["E703"] = [['⟦E703⟧print("Done");'], ["<<n1>> = 5", "⟦E703⟧print(<<n1>>);"],
             ['⟦E703⟧print("-" * 10);'], ["⟦E703⟧<<n1>> = 7;", "print(<<n1>>)"],
             ['<<n1>> = "ok"', "⟦E703⟧print(<<n1>>.upper());"]]
T["E711"] = [["<<n1>> = None", "⟦E711⟧if <<n1>> == None:", '    print("nothing yet")'],
             ["<<n1>> = 5", "⟦E711⟧if <<n1>> != None:", '    print("has a value")'],
             ["<<n1>> = None", "⟦E711⟧if None == <<n1>>:", '    print("empty")'],
             ["<<n1>> = [1]", "⟦E711⟧print(<<n1>> == None)"],
             ['<<n1>> = ""', "⟦E711⟧while <<n1>> != None:", "    break"]]
T["E712"] = [["<<n1>> = True", "⟦E712⟧if <<n1>> == True:", '    print("ready")'],
             ["<<n1>> = False", "⟦E712⟧if <<n1>> == False:", '    print("not ready")'],
             ["<<n1>> = True", "⟦E712⟧if <<n1>> != True:", '    print("off")'],
             ["<<n1>> = True", "⟦E712⟧print(<<n1>> == True)"],
             ["<<n1>> = False", "⟦E712⟧if True == <<n1>>:", '    print("on")']]
T["E713"] = [['<<n1>> = ["apple", "pear"]', '⟦E713⟧if not "kiwi" in <<n1>>:', '    print("no kiwi")'],
             ['<<n1>> = "hello"', '⟦E713⟧if not "z" in <<n1>>:', '    print("no z")'],
             ['<<n1>> = {"a": 1}', '⟦E713⟧if not "b" in <<n1>>:', '    print("no b")'],
             ["<<n1>> = (1, 2, 3)", "⟦E713⟧if not 4 in <<n1>>:", '    print("no 4")'],
             ['<<n1>> = ["x"]', '⟦E713⟧print(not "y" in <<n1>>)']]
T["E714"] = [['<<n1>> = "pen"', "⟦E714⟧if not <<n1>> is None:", '    print("has item")'],
             ["<<n1>> = 3", "⟦E714⟧if not <<n1>> is None:", '    print("number set")'],
             ["<<n1>> = []", "⟦E714⟧print(not <<n1>> is None)"],
             ['<<n1>> = "a"', "⟦E714⟧if not <<n1>> is None and <<n1>>:", '    print("ok")'],
             ["<<n1>> = 0", "⟦E714⟧while not <<n1>> is None:", "    break"]]
T["E721"] = [["<<n1>> = 3", "<<n2>> = 4.5", "⟦E721⟧if type(<<n1>>) == type(<<n2>>):", '    print("same type")'],
             ['<<n1>> = "a"', "⟦E721⟧if type(<<n1>>) == str:", '    print("text")'],
             ["<<n1>> = 1", "⟦E721⟧if type(<<n1>>) != int:", '    print("not int")'],
             ["<<n1>> = [1]", "⟦E721⟧print(type(<<n1>>) == list)"],
             ["<<n1>> = 2.5", "⟦E721⟧if type(<<n1>>) == float:", '    print("float")']]
T["E722"] = [["try:", '    <<n1>> = int("42")', "    print(<<n1>>)", "⟦E722⟧except:", '    print("not a number")'],
             ["try:", "    print(10 / 0)", "⟦E722⟧except:", '    print("math error")'],
             ["try:", "    <<n1>> = [1, 2]", "    print(<<n1>>[5])", "⟦E722⟧except:", '    print("bad index")'],
             ["try:", '    print(int("x"))', "⟦E722⟧except:", "    pass"],
             ["try:", '    <<n1>> = {"a": 1}', '    print(<<n1>>["b"])', "⟦E722⟧except:", '    print("missing key")']]
T["E731"] = [["⟦E731⟧<<n1>> = lambda x: x * x", "print(<<n1>>(3))"],
             ["⟦E731⟧<<n1>> = lambda a, b: a + b", "print(<<n1>>(1, 2))"],
             ["⟦E731⟧<<n1>> = lambda s: s.upper()", 'print(<<n1>>("hi"))'],
             ["⟦E731⟧<<n1>> = lambda: 42", "print(<<n1>>())"],
             ["⟦E731⟧<<n1>> = lambda n: n % 2 == 0", "print(<<n1>>(4))"]]
T["E741"] = [["⟦E741⟧l = [3, 6, 9]", "print(len(l))"], ["⟦E741⟧O = 0", "print(O + 1)"],
             ["⟦E741⟧for I in range(3):", "    print(I)"], ['⟦E741⟧l = "text"', "print(l.upper())"],
             ["⟦E741⟧I = 5", "print(I * 2)"]]
E741_ABSENT = [["l"], ["O"], ["I"], ["l"], ["I"]]
T["W605"] = [[r'⟦W605⟧print("Digit:", "\d")'], [r'⟦W605⟧print("Word:", "\w")'],
             [r'⟦W605⟧print("Space:", "\s")'], [r'⟦W605⟧print("Dot:", "a\.b")'],
             [r'⟦W605⟧print("Paren:", "\(")']]
T["W191"] = [["<<n1>> = 3", "if <<n1>> > 1:", '⟦W191⟧\tprint("big")'],
             ["for <<n1>> in range(2):", "⟦W191⟧\tprint(<<n1>>)"], ["while False:", "⟦W191⟧\tbreak"],
             ['<<n1>> = "a"', "if <<n1>>:", "⟦W191⟧\tprint(<<n1>>)"],
             ['for <<n1>> in "ab":', "⟦W191⟧\tprint(<<n1>>)"]]
F401_V = [("import os", ["os"]), ("import sys", ["sys"]), ("import re", ["re"]),
          ("from collections import Counter", ["Counter"]), ("from pathlib import Path", ["Path"]),
          ("import time", ["time"]), ("from typing import List", ["List"]), ("import csv", ["csv"]),
          ("from itertools import chain", ["chain"]), ("import os.path", ["os"]),
          ("from functools import reduce", ["reduce"]), ("import shutil", ["shutil"])]
E401_V = [("import os, sys", ["os", "sys"], "print(os.sep, sys.byteorder)"),
          ("import string, time", ["string", "time"], "print(string.digits, time.timezone)"),
          ("import json, csv", ["json", "csv"], "print(json.dumps([1, 2]), csv.QUOTE_ALL)"),
          ("import platform, calendar", ["platform", "calendar"], "print(platform.system(), calendar.isleap(2024))"),
          ("import keyword, heapq", ["keyword", "heapq"], 'print(keyword.iskeyword("if"), heapq.nsmallest(1, [3, 1]))')]
E402_V = [("import string", ["string"], "print(string.ascii_lowercase[:3])"),
          ("import time", ["time"], "print(time.timezone)"), ("import os", ["os"], "print(os.sep)"),
          ("import sys", ["sys"], "print(sys.byteorder)"), ("import csv", ["csv"], "print(csv.QUOTE_ALL)")]
F811_NAMES = ["show_line", "divider", "greet_user", "say_hello", "draw_line", "banner",
              "print_header", "separator"]

RULES = ["F401", "F811", "F821", "F841", "F541", "F632", "E401", "E402", "E501", "E701", "E702",
         "E703", "E711", "E712", "E713", "E714", "E721", "E722", "E731", "E741", "W191", "W291",
         "W292", "W293", "W605"]
LOC_CYCLE = ["main", "func", "method"]
RESTRICT = {"F841": ["func", "method"], "W191": ["main"]}

# ---------------------------------------------------------------- applying edits
def insert(p, loc, s, rng):
    if loc == "main":
        p["main"].insert(rng.randint(0, len(p["main"])), s)
        return
    body = p["fbody"] if loc == "func" else p["cls"]["mbody"]
    lo = 1 if body and body[0].t.lstrip().startswith('"""') else 0
    hi = len(body) - 1 if body and body[-1].t.lstrip().startswith("return") else len(body)
    body.insert(rng.randint(lo, hi), s)


def long_line(rng, kind):
    while True:
        if kind == 0:
            words = [rng.choice(FILLER) for _ in range(rng.randint(17, 20))]
            line = "# " + " ".join(words)
        elif kind == 1:
            words = [rng.choice(FILLER) for _ in range(rng.randint(17, 20))]
            line = 'print("' + " ".join(words) + '")'
        elif kind == 2:
            line = "print([" + ", ".join(str(rng.randint(10, 99)) for _ in range(rng.randint(24, 28))) + "])"
        elif kind == 3:
            w = [rng.choice(WORDS) for _ in range(5)]
            line = f'print("Name:", "{w[0]}", "City:", "{w[1]}", "Note:", "{w[2]} {w[3]} {w[4]} and more text")'
        else:
            words = [rng.choice(FILLER) for _ in range(rng.randint(17, 20))]
            line = '"""' + " ".join(words) + '"""'
        if 92 <= len(line) <= 112:
            return line


def apply_rule(p, rule, count, loc, rng):
    """Edit p in place; return expectations [(rule, S or None, line_offset)]."""
    cur = compose(p)[0]
    v = count[rule]
    count[rule] += 1
    if rule == "F401":
        for k in range(len(F401_V)):
            line, absent = F401_V[(v + k) % len(F401_V)]
            if not any(has_word(cur, a) for a in absent):
                s = S(line)
                p["imports"].insert(rng.randint(0, len(p["imports"])), s)
                return [("F401", s, 0)]
        raise RuntimeError("no F401 variant")
    if rule == "E401":
        for k in range(len(E401_V)):
            line, absent, use = E401_V[(v + k) % len(E401_V)]
            if not any(has_word(cur, a) for a in absent):
                s = S(line)
                p["imports"].insert(rng.randint(0, len(p["imports"])), s)
                p["main"].insert(rng.randint(0, len(p["main"])), S(use))
                return [("E401", s, 0)]
        raise RuntimeError("no E401 variant")
    if rule == "E402":
        for k in range(len(E402_V)):
            line, absent, use = E402_V[(v + k) % len(E402_V)]
            if not any(has_word(cur, a) for a in absent):
                s = S(line)
                idx = rng.randint(0, len(p["main"]))
                p["main"].insert(idx, s)
                p["main"].insert(idx + 1, S(use))
                return [("E402", s, 0)]
        raise RuntimeError("no E402 variant")
    if rule == "F811":
        name = pick_names(rng, cur, F811_NAMES, 1)[0]
        a, b = S(f'def {name}():\n    print("-" * 20)'), S(f'def {name}():\n    print("=" * 20)')
        p["between"] += [a, b]
        return [("F811", b, 0)]
    if rule == "W292":
        p["eof_nl"] = False
        return [("W292", None, 0)]
    if rule == "W293":
        s = S(" " * (1 + v % 4) if loc == "main" else "    ")
        insert(p, "main" if loc not in ("func",) else "func", s, rng)
        return [("W293", s, 0)]
    if rule == "W291":
        pool = list(p["imports"]) + list(p["fbody"]) + list(p["main"])
        if p["cls"]:
            pool += p["cls"]["mbody"]
        pool = [s for s in pool if s.t.strip() and not s.t.lstrip().startswith('"""')]
        s = rng.choice(pool)
        first, _, rest = s.t.partition("\n")
        s.t = first + [" ", "  ", "    ", "\t"][v % 4] + (("\n" + rest) if rest else "")
        return [("W291", s, 0)]
    if rule == "E501":
        text = long_line(rng, v % 5)
        ind = {"main": "", "func": "    ", "method": "        "}[loc]
        s = S(ind + text)
        insert(p, loc, s, rng)
        assert len(ind + text) > 88
        return [("E501", s, 0)]
    # template-based rules
    variants = T[rule]
    lines = variants[v % len(variants)]
    names = {}
    if any("<<n1>>" in l or "<<N1>>" in l for l in lines):
        n = pick_names(rng, cur, VARS, 2)
        names = {"n1": n[0], "n2": n[1], "N1": n[0].capitalize()}
    if any("<<t1>>" in l for l in lines):
        names["t1"] = pick_names(rng, cur, TYPOS, 1)[0]
    if rule == "E741" and any(has_word(cur, a) for a in E741_ABSENT[v % 5]):
        raise RuntimeError("E741 name clash")
    ind = {"main": "", "func": "    ", "method": "        "}[loc]
    out, exp = [], []
    for i, l in enumerate(lines):
        m = MARK.match(l)
        if m:
            exp.append((m.group(1), i))
            l = l[m.end():]
        for key, val in names.items():
            l = l.replace(f"<<{key}>>", val)
        out.append(ind + l)
    s = S("\n".join(out))
    insert(p, loc, s, rng)
    return [(r, s, off) for r, off in exp]


# ---------------------------------------------------------------- measuring (independent of the app)
def cc_of(fn):
    c = 1
    for n in ast.walk(fn):
        if n is fn:
            continue
        if isinstance(n, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.Assert)):
            c += 1
        if isinstance(n, (ast.For, ast.While)) and n.orelse:
            c += 1
        if isinstance(n, ast.BoolOp):
            c += len(n.values) - 1
        if isinstance(n, ast.comprehension):
            c += 1 + len(n.ifs)
        if isinstance(n, ast.Lambda):
            c += 1
    return c


def functions_cc(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    return [(n.name, cc_of(n)) for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def flagged(text):
    return sorted(n for n, c in functions_cc(text) if c >= FLAG_AT)


# ---------------------------------------------------------------- case collection
CASES = []  # dicts: file, group, design, text (str or bytes), expected, flagged, syntax


def add_case(name, group, design, text, expected, syntax=False, raw=None):
    data = raw if raw is not None else text.encode("utf-8")
    if raw is None:
        fl = [] if syntax else flagged(text)
    else:
        fl = flagged(raw.decode("utf-8", "replace").replace("\r\n", "\n"))
    CASES.append({"file": name, "group": group, "design": design, "bytes": data,
                  "expected": sorted(expected), "flagged": fl, "syntax": syntax})


def build():
    rng = random.Random(SEED)
    order = BASE_NAMES[:]
    rng.shuffle(order)
    count = Counter()
    k = 0  # global base cursor so every base is used almost equally often

    def make_flawed(rules, tag, group, idx):
        nonlocal k
        for attempt in range(8):
            name = order[k % len(order)]
            p = clone(BASES[name])
            sub = random.Random(SEED * 1000 + idx * 17 + attempt)
            saved = Counter(count)
            exp_all, locs = [], []
            try:
                for rule in rules:
                    allowed = RESTRICT.get(rule, LOC_CYCLE)
                    loc = allowed[(count[rule] + attempt) % len(allowed)]
                    if loc == "method" and not p["cls"]:
                        loc = "func"
                    if attempt >= 4 and rule not in RESTRICT:
                        loc = "main"
                    exp = apply_rule(p, rule, count, loc, sub)
                    exp_all += exp
                    locs.append(loc)
                text, pos = compose(p)
                if any(c > 5 for _, c in functions_cc(text)):
                    raise RuntimeError("complexity above 5 in a non-complexity case")
                compile(text, "<x>", "exec")
            except (RuntimeError, SyntaxError):
                count.clear()
                count.update(saved)
                k += 1
                continue
            k += 1
            expected = []
            for r, s, off in exp_all:
                line = len(text.split("\n")) if s is None else pos[s.id] + off
                expected.append((r, line))
            add_case(f"{tag}.py", group, f"base={name}; rules={'+'.join(rules)}; where={'+'.join(locs)}", text, expected)
            return
        raise RuntimeError(f"could not build {tag}")

    idx = 0
    for r_i, rule in enumerate(RULES):
        for j in range(10):
            idx += 1
            make_flawed([rule], f"single_{rule.lower()}_{j + 1:02d}", "single", idx)
    for i in range(25):
        idx += 1
        triple = [RULES[(i + a * 8) % 25] for a in range(3)]
        make_flawed(triple, f"multi_{i + 1:02d}", "multi", idx)

    # clean controls: the bases as they are, and neutral edits of them
    for name in BASE_NAMES:
        text, _ = compose(BASES[name])
        add_case(f"clean_{name}.py", "clean", f"base={name}", text, [])
    NEUTRAL = ["# print the result for the reader", "# a small practice program",
               "# check the output by hand", "# see the course notes for details"]
    for i, name in enumerate(BASE_NAMES):
        p = clone(BASES[name])
        sub = random.Random(SEED + 500 + i)
        n_edits = 1 + i % 4
        for e in range(n_edits):
            kind = (i + e) % 3
            if kind == 0:
                p["main"].insert(sub.randint(0, len(p["main"])), S(NEUTRAL[(i + e) % 4]))
            elif kind == 1:
                p["main"].append(S('print("Done")'))
            else:
                p["main"].append(S('print("-" * 20)'))
        if i % 3 == 0:
            p["modedoc"] = '"""Small practice program."""'
        text, _ = compose(p)
        add_case(f"clean_{name}_variant.py", "clean", f"base={name}; neutral edits={n_edits}", text, [])

    # near-miss controls: code that looks suspicious but is correct
    for i, text in enumerate(NEAR_MISS):
        add_case(f"nearmiss_{i + 1:02d}.py", "near_miss", "correct code that resembles a common mistake", text.strip("\n") + "\n", [])

    # syntax errors
    def syn(kind, j, base_name):
        p = clone(BASES[base_name])
        text, _ = compose(p)
        lines = text.split("\n")
        if kind == "missing_colon":
            cands = [i for i, l in enumerate(lines) if l.rstrip().endswith(":")]
            if not cands:
                return None
            i = cands[j % len(cands)]
            lines[i] = lines[i].rstrip()[:-1]
        elif kind == "unclosed_paren":
            cands = [i for i, l in enumerate(lines) if "print(" in l and l.rstrip().endswith(")")]
            if not cands:
                return None
            i = cands[j % len(cands)]
            lines[i] = lines[i].rstrip()[:-1]
        elif kind == "unterminated_string":
            cands = [i for i, l in enumerate(lines) if "print(" in l and '"' in l]
            if not cands:
                return None
            i = cands[j % len(cands)]
            q = lines[i].rindex('"')
            lines[i] = lines[i][:q] + lines[i][q + 1:]
        elif kind == "unexpected_indent":
            cands = [i for i, l in enumerate(lines) if l and not l.startswith((" ", "\t", "def ", "class ", "import ", "from "))]
            if not cands:
                return None
            i = cands[j % len(cands)]
            lines[i] = "    " + lines[i]
        elif kind == "missing_block":
            hdr = ["if True:", "for _ in range(2):", "while False:"][j % 3]
            lines += [hdr, 'print("checked")']
        elif kind == "return_outside":
            lines += [["return 0", "return total", "return None"][j % 3]]
        elif kind == "python2_print":
            lines += [['print "Hello"', 'print "Total:", 5', 'print "done"'][j % 3]]
        elif kind == "bad_assignment":
            lines += [["5 = number", "total + 1 = 10", '"name" = value'][j % 3]]
        text = "\n".join(lines)
        text = text if text.endswith("\n") else text + "\n"
        try:
            compile(text, "<x>", "exec")
        except SyntaxError:
            return text
        return None

    kinds = ["missing_colon", "unclosed_paren", "unterminated_string", "unexpected_indent",
             "missing_block", "return_outside", "python2_print", "bad_assignment"]
    n = 0
    for ki, kind in enumerate(kinds):
        for j in range(3):
            for extra in range(len(order)):
                bn = order[(n * 5 + extra) % len(order)]
                text = syn(kind, j, bn)
                if text:
                    add_case(f"syntax_{kind}_{j + 1}.py", "syntax", f"kind={kind}; base={bn}", text, [], syntax=True)
                    break
            else:
                raise RuntimeError("syntax case failed " + kind)
            n += 1

    # complexity bands
    blocks = {
        "if": (1, lambda r: f"    if n > {r.randint(1, 9)}:\n        total += {r.randint(1, 9)}"),
        "for": (1, lambda r: f"    for i in range({r.randint(2, 9)}):\n        total += i"),
        "while": (1, lambda r: f"    while total < {r.randint(5, 50)}:\n        total += 1"),
        "try": (1, lambda r: "    try:\n        total += int(str(n))\n    except ValueError:\n        total -= 1"),
        "if_and": (2, lambda r: f"    if n > {r.randint(1, 9)} and n % 2 == 0:\n        total += 1"),
        "if_or": (2, lambda r: f"    if n < {r.randint(1, 5)} or n > {r.randint(20, 90)}:\n        total -= 1"),
        "for_if": (2, lambda r: f"    for i in range({r.randint(3, 9)}):\n        if i % 2 == 0:\n            total += i"),
        "chain3": (3, lambda r: f"    if n == {r.randint(1, 5)}:\n        total += 1\n    elif n == {r.randint(6, 9)}:\n        total += 2\n    elif n == {r.randint(10, 15)}:\n        total += 3"),
    }
    FN_NAMES = ["score_player", "grade_entry", "shipping_cost", "ticket_price", "risk_level",
                "discount", "bonus_points", "late_fee", "rank_team", "tax_class", "weather_score",
                "parking_fee", "age_group", "level_up", "stock_alert", "mail_priority",
                "route_cost", "meal_plan", "quiz_points", "energy_use", "rent_tier", "fine_amount",
                "badge_level", "seat_price"]
    targets = [1, 2, 3, 4, 4, 5, 5, 5, 5, 3, 2, 5, 6, 6, 6, 6, 7, 7, 8, 9, 10, 12, 15, 20]
    rng2 = random.Random(SEED + 99)
    for i, target in enumerate(targets):
        while True:
            remaining, chosen = target - 1, []
            while remaining > 0:
                opts = [b for b, (c, _) in blocks.items() if c <= remaining]
                b = rng2.choice(opts)
                chosen.append(blocks[b][1](rng2))
                remaining -= blocks[b][0]
            name = FN_NAMES[i]
            body = "\n".join(chosen)
            text = f"def {name}(n):\n    total = 0\n" + (body + "\n" if body else "") + f"    return total\n\n\nprint({name}(7))\n"
            if dict(functions_cc(text)).get(name) == target:
                break
        add_case(f"complexity_{i + 1:02d}_cc{target}.py", "complexity", f"target complexity={target}", text, [])

    # edge cases and robustness
    add_case("edge_empty.py", "edge", "empty file (0 bytes)", "", [])
    add_case("edge_only_comments.py", "edge", "comments only", "# nothing here yet\n# just notes\n", [])
    add_case("edge_only_docstring.py", "edge", "docstring only", '"""A module with only a docstring."""\n', [])
    add_case("edge_only_pass.py", "edge", "only pass", "pass\n", [])
    add_case("edge_umlauts.py", "edge", "German text and identifiers", 'größe = 3\nname = "Müller"\nprint("Grüße,", name, größe)\n', [])
    crlf = 'name = "Ada"\r\nprint("Hello,", name)\r\n'
    add_case("edge_crlf_clean.py", "edge", "Windows line endings, clean", "", [], raw=crlf.encode())
    crlf2 = 'import os\r\nname = "Ada"\r\nprint("Hello,", name)\r\n'
    add_case("edge_crlf_unused_import.py", "edge", "Windows line endings, one finding", "", [("F401", 1)], raw=crlf2.encode())

    def big(n_funcs):
        out = []
        for i in range(n_funcs):
            out.append(f'def calc_{i}(x):\n    """Return a small calculation for example {i}."""\n    total = 0\n'
                       f"    for step in range({i % 7 + 1}):\n        total += x * step\n    return total\n\n")
        out.append("\nprint(" + " + ".join(f"calc_{i}(2)" for i in range(min(n_funcs, 5))) + ")\n")
        return "\n".join(out)
    for label, n_funcs in (("100_lines", 12), ("500_lines", 60), ("2000_lines", 240)):
        t = big(n_funcs)
        add_case(f"edge_size_{label}.py", "edge", f"clean file of about {label.split('_')[0]} lines (runtime scaling)", t, [])


NEAR_MISS = [
    'value = None\nif value is None:\n    print("empty")\nelse:\n    print(value)\n',
    'names = ["Mia", "Ben", "Zoe"]\nprint(sorted(names, key=lambda name: name.lower()))\n',
    'number = 3\nif type(number) is int:\n    print("whole number")\n',
    'import re\n\npattern = r"\\d+\\.\\d+"\nprint(re.findall(pattern, "pi is 3.14"))\n',
    '# docs: https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex-and-more-text\nprint("see the docs")\n',
    'import os  # noqa: F401\n\nprint("hello")\n',
    'for _ in range(3):\n    print("hi")\n',
    'try:\n    number = int("x")\nexcept ValueError as error:\n    print("bad number:", error)\n',
    'name = "Ada"\nprint(f"Hello, {name}")\n',
    '_ = input("Press enter to continue")\nprint("thanks")\n',
    'class Dog:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return self.name + " says woof"\n\n\nprint(Dog("Rex").speak())\n',
    'ready = True\nif ready is True:\n    print("go")\n',
    'basket = ["apple", "pear"]\nif "kiwi" not in basket:\n    print("no kiwi")\n',
    'item = "pen"\nif item is not None:\n    print("has item")\n',
    'def make_counter():\n    count = 0\n\n    def increment():\n        nonlocal count\n        count += 1\n        return count\n\n    return increment\n\n\ncounter = make_counter()\nprint(counter(), counter())\n',
    'TOTAL = 0\n\n\ndef add(amount):\n    global TOTAL\n    TOTAL += amount\n\n\nadd(5)\nprint(TOTAL)\n',
    'def greet(name, greeting="Hello", punctuation="!"):\n    return greeting + ", " + name + punctuation\n\n\nprint(greet("Ada", punctuation="?"))\n',
    'def read_lines(path):\n    with open(path, encoding="utf-8") as handle:\n        return handle.readlines()\n\n\nprint("reader ready")\n',
    'def total(*numbers):\n    return sum(numbers)\n\n\nprint(total(1, 2, 3))\n',
    'try:\n    value = int("5")\nexcept ValueError:\n    print("not a number")\nelse:\n    print(value * 2)\nfinally:\n    print("done")\n',
]


# ---------------------------------------------------------------- verification and card
def ruff_findings(data):
    r = subprocess.run(["ruff", "check", "--isolated", "--no-cache", "--select", "E,F,W",
                        "--output-format", "json", "--stdin-filename", "x.py", "-"],
                       input=data, capture_output=True)
    return sorted((d["code"], d["location"]["row"]) for d in json.loads(r.stdout or b"[]"))


def verify():
    problems = []
    for c in CASES:
        data = c["bytes"]
        text = data.decode("utf-8")
        try:
            compile(text, "<x>", "exec")
            ok = True
        except (SyntaxError, ValueError):
            ok = False
        if ok == c["syntax"]:
            problems.append((c["file"], "syntax flag", c["syntax"], ok))
            continue
        if ok:
            got = ruff_findings(data)
            if got != c["expected"]:
                problems.append((c["file"], "ruff differs", c["expected"], got))
    return problems


def card(problems):
    g = defaultdict(list)
    for c in CASES:
        g[c["group"]].append(c)
    rules = Counter(r for c in CASES for r, _ in c["expected"])
    bases = Counter(re.search(r"base=(\w+)", c["design"]).group(1) for c in CASES
                    if c["group"] in ("single", "multi") and "base=" in c["design"])
    locs = Counter()
    for c in g["single"] + g["multi"]:
        m = re.search(r"where=([\w+]+)", c["design"])
        for w in m.group(1).split("+"):
            locs[w] += 1
    lines = [c["bytes"].decode("utf-8", "replace").count("\n") for c in CASES]
    def med(grp):
        v = [c["bytes"].decode("utf-8", "replace").count("\n") for c in g[grp]]
        return statistics.median(v) if v else 0
    fl_pos = sum(len(c["flagged"]) for c in CASES if c["group"] == "complexity")
    fl_cases = sum(1 for c in g["complexity"] if c["flagged"])
    out = ["# Generated evaluation set: dataset card", "",
           f"{len(CASES)} files. Built by `generate_dataset.py` (seed {SEED}); regenerating gives identical files.", "",
           "## How the labels were made",
           f"- {len(BASE_NAMES)} clean beginner programs (the *bases*) were written first; every base is verified to have no findings.",
           "- Each flawed case applies one documented edit to a base (or three edits for the `multi` group). "
           "The expected rule and line come from the edit, not from any tool's output.",
           "- Ruff, `compile()` and a complexity counter were run afterwards only to catch design mistakes. "
           f"Disagreements found: {len(problems)}.",
           "", "",
           "## Balance",
           f"- Rules covered: {len(rules)}. Expected findings per rule (min {min(rules.values())}, max {max(rules.values())}):",
           "  " + ", ".join(f"{r} {n}" for r, n in sorted(rules.items())),
           f"- Every base program is used in flawed cases between {min(bases.values())} and {max(bases.values())} times (of {len(BASE_NAMES)} bases).",
           f"- Where the edit sits (single and multi cases): {dict(locs)}. Edits inside class methods are rare because only 2 of the {len(BASE_NAMES)} bases contain a class.",
           "- Groups: " + ", ".join(f"{k} {len(v)}" for k, v in g.items()) + ".",
           f"- Complexity group: {fl_cases} of {len(g['complexity'])} files contain a function with a score of {FLAG_AT} or more.",
           f"- Median file length (lines): clean {med('clean')}, single {med('single')}, multi {med('multi')}, "
           f"syntax {med('syntax')}, complexity {med('complexity')}. Flawed and clean files have similar lengths, "
           "so file length does not give the answer away.", "",
           "## Known limits",
           "- Rule coverage is 25 of the many E, F and W rules; they were chosen as common beginner mistakes.",
           "- Programs are shor; real-world files are covered separately by `eval_data/real`.",
           "- Findings inside class bodies are covered only for methods; nested functions, async code and decorators are not covered.",
           "- Complexity labels follow Radon's documented counting rules and were counted by script, not by running Radon."]
    return "\n".join(out) + "\n"


def main():
    build()
    problems = verify()
    OUT.mkdir(parents=True, exist_ok=True)
    for c in CASES:
        (OUT / c["file"]).write_bytes(c["bytes"])
    labels = {"label_method": "Generated by generate_dataset.py. Expected findings come from the edit that creates each case; "
                              "Ruff/compile()/a complexity counter were run afterwards only to catch design mistakes.",
              "cases": [{"file": c["file"], "labelled": True, "group": c["group"], "design": c["design"],
                         "expected": [{"rule": r, "line": ln} for r, ln in c["expected"]],
                         "flagged_functions": c["flagged"], "syntax_error": c["syntax"]} for c in CASES]}
    (OUT / "labels_generated.json").write_text(json.dumps(labels, indent=2), encoding="utf-8")
    (OUT / "DATASET_CARD.md").write_text(card(problems), encoding="utf-8")
    print(len(CASES), "cases;", len(problems), "design problems")
    for p in problems[:40]:
        print(p)


if __name__ == "__main__":
    main()
