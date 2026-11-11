from overview import clean_text, describe_code, escape_markdown


def overview(code):
    result, error = describe_code(code)
    assert error is None
    return result


GREET = '''"""A tiny greeter."""
import os
from math import sqrt


def greet(name, times=3, *args, **kwargs):
    """Say hello."""
    for _ in range(times):
        print("hi", name)


def add(a, b):
    return a + b


def main():
    greet("World")
    total = add(1, 2)
    if total:
        return total


if __name__ == "__main__":
    main()
'''


def test_empty_code_gives_empty_overview():
    o = overview("")
    assert o.functions == [] and o.classes == [] and o.imports == []
    assert o.line_count == 0 and o.code_line_count == 0


def test_counts_functions_and_code_lines():
    o = overview(GREET)
    assert [f.name for f in o.functions] == ["greet", "add", "main"]
    assert o.code_line_count < o.line_count  # blank lines and comments are not code lines


def test_parameters_and_defaults_are_listed():
    greet = overview(GREET).functions[0]
    assert greet.params == ["name", "times=3", "*args", "**kwargs"]
    assert greet.signature == "greet(name, times=3, *args, **kwargs)"


def test_return_detection():
    funcs = {f.name: f for f in overview(GREET).functions}
    assert funcs["add"].returns_value is True
    assert funcs["greet"].returns_value is False
    assert "does not return a value" in funcs["greet"].summary()


def test_bare_return_and_return_none_do_not_count_as_returning_a_value():
    o = overview("def a():\n    return\n\n\ndef b():\n    return None\n")
    assert [f.returns_value for f in o.functions] == [False, False]


def test_prints_loops_and_decisions_are_noticed():
    funcs = {f.name: f for f in overview(GREET).functions}
    assert funcs["greet"].prints and funcs["greet"].loops
    assert funcs["main"].decisions
    assert not funcs["add"].prints


def test_function_calling_your_own_functions_is_noticed():
    main = overview(GREET).functions[2]
    assert main.calls_own == ["greet", "add"]
    assert "uses greet, add" in main.summary()


def test_recursion_does_not_list_itself():
    f = overview("def f(n):\n    return f(n - 1)\n").functions[0]
    assert f.calls_own == []


def test_docstring_first_line_is_kept():
    o = overview(GREET)
    assert o.functions[0].doc == "Say hello."
    assert o.module_doc == "A tiny greeter."


def test_generator_is_described_as_one_at_a_time():
    f = overview("def count():\n    yield 1\n    yield 2\n").functions[0]
    assert f.is_generator and "one at a time" in f.summary()
    assert "does not return a value" not in f.summary()


def test_input_and_open_are_noticed():
    o = overview("def f():\n    name = input('x')\n    open('a.txt')\n")
    f = o.functions[0]
    assert f.reads_input and f.opens_files
    assert any("input()" in n for n in o.notes) and any("open()" in n for n in o.notes)


def test_eval_and_exec_get_a_warning_note():
    o = overview("eval('1 + 1')\n")
    assert any("eval() or exec()" in n for n in o.notes)


def test_nested_function_is_not_mixed_into_the_outer_one():
    o = overview("def outer():\n    def inner():\n        print('x')\n    return 1\n")
    assert [f.name for f in o.functions] == ["outer"]
    assert o.functions[0].prints is False  # the print belongs to inner


def test_methods_skip_self_and_are_named_with_their_class():
    o = overview('class Calc(Base):\n    """Does sums."""\n\n    def add(self, a, b):\n        return a + b\n')
    assert [f.name for f in o.functions] == ["Calc.add"]
    assert o.functions[0].params == ["a", "b"]
    c = o.classes[0]
    assert c.name == "Calc" and c.bases == ["Base"] and c.methods == ["add"] and c.doc == "Does sums."


def test_async_and_decorated_functions():
    o = overview("@cache\nasync def fetch(url):\n    return url\n")
    f = o.functions[0]
    assert f.is_async and f.decorators == ["cache"]


def test_imports_are_classified():
    o = overview("import os\nimport requests\nfrom . import helper\nfrom math import sqrt\nimport os\n")
    kinds = {i.text: i.kind for i in o.imports}
    assert kinds["import os"] == "standard library"
    assert kinds["import requests"] == "external package or your own module"
    assert kinds["from . import helper"] == "same project"
    assert kinds["from math import sqrt"] == "standard library"
    assert len(o.imports) == 4  # the duplicate "import os" is listed once
    assert [i.purpose for i in o.imports if i.text == "import os"] == ["operating-system tasks such as files and folders"]


def test_top_level_calls_and_main_guard():
    o = overview(GREET)
    assert o.has_main_guard is True
    assert o.top_level_calls == ["main"]
    o2 = overview("def f():\n    pass\n\n\nresult = f()\nprint(result)\n")
    assert o2.has_main_guard is False and o2.top_level_calls == ["f", "print"]


def test_syntax_error_is_returned_not_raised():
    result, error = describe_code("def f(:\n")
    assert result is None and error is not None


def test_null_byte_does_not_crash():
    result, error = describe_code("x = 1\0\n")
    assert result is None and error is not None


def test_long_defaults_are_shortened_and_backticks_removed():
    f = overview("def f(x='" + "a" * 100 + "`b'):\n    pass\n").functions[0]
    assert len(f.params[0]) < 40 and "`" not in f.params[0]
    assert "`" not in clean_text("a`b")


def test_markdown_in_user_text_is_neutralised():
    escaped = escape_markdown("[click](http://x) :red[hi] $x$ <b>")
    for risky in ("[", "]", "(", ")", "<", ">", "$", ":"):
        assert "\\" + risky in escaped


def test_code_is_never_executed(tmp_path):
    marker = tmp_path / "marker.txt"
    code = f"open({str(marker)!r}, 'w').write('ran')\n"
    describe_code(code)
    assert not marker.exists()


def test_input_wording_handles_optional_and_extra_inputs():
    funcs = {f.name: f for f in overview(GREET).functions}
    assert "takes 2 inputs (1 optional), plus any number of extra inputs" in funcs["greet"].summary()
    assert "takes 2 inputs;" in funcs["add"].summary()
    assert overview("def f():\n    pass\n").functions[0].summary().startswith("takes no inputs")
    assert overview("def f(x):\n    pass\n").functions[0].summary().startswith("takes 1 input;")