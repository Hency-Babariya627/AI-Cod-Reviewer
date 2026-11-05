from analyzers import radon_check
from analyzers.radon_check import FLAG_THRESHOLD, analyze_complexity

SIMPLE = "def add(a, b):\n    return a + b\n"

BRANCHY = """def grade(score, bonus, late):
    if score > 90:
        return "A"
    elif score > 80:
        return "B"
    elif score > 70:
        return "C"
    elif score > 60:
        return "D"
    for i in range(bonus):
        if i > 3 and late:
            score += 1
    return "F"
"""


def test_simple_function_is_rank_a_not_flagged():
    results, error = analyze_complexity(SIMPLE)
    assert error is None
    assert len(results) == 1
    assert results[0].name == "add"
    assert results[0].complexity == 1
    assert results[0].rank == "A"
    assert results[0].flagged is False


def test_branchy_function_is_flagged():
    results, error = analyze_complexity(BRANCHY)
    assert error is None
    assert results[0].name == "grade"
    assert results[0].complexity >= FLAG_THRESHOLD
    assert results[0].flagged is True
    assert "helper" in results[0].suggestion


def test_empty_code_has_no_functions():
    results, error = analyze_complexity("")
    assert error is None
    assert results == []


def test_code_without_functions_has_no_results():
    results, error = analyze_complexity("x = 1\nprint(x)\n")
    assert error is None
    assert results == []


def test_methods_are_named_with_class():
    code = "class Calc:\n    def add(self, a, b):\n        return a + b\n"
    results, error = analyze_complexity(code)
    assert error is None
    assert [r.name for r in results] == ["Calc.add"]


def test_results_sorted_most_complex_first():
    results, _ = analyze_complexity(SIMPLE + "\n" + BRANCHY)
    assert [r.name for r in results] == ["grade", "add"]


def test_syntax_error_is_reported_not_hidden():
    results, error = analyze_complexity("def f(:\n")
    assert results == []
    assert error is not None


def test_unexpected_failure_is_reported(monkeypatch):
    def boom(code):
        raise RuntimeError("boom")

    monkeypatch.setattr(radon_check, "cc_visit", boom)
    results, error = analyze_complexity("x = 1\n")
    assert results == []
    assert "boom" in error


def test_code_is_never_executed(tmp_path):
    marker = tmp_path / "marker.txt"
    code = f"open({str(marker)!r}, 'w').write('ran')\n"
    analyze_complexity(code)
    assert not marker.exists()