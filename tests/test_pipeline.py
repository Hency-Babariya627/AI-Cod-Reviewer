import pipeline
from pipeline import review_code


def test_clean_code():
    code = "def add(a, b):\n    return a + b\n"
    result = review_code(code)
    assert result.code == code
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.style_count == 0
    assert result.ruff_error is None
    assert result.ruff_skipped is False
    assert len(result.complexity) == 1


def test_empty_code():
    result = review_code("")
    assert result.error_count == 0
    assert result.complexity == []
    assert result.ruff_error is None


def test_syntax_error_skips_other_tools():
    result = review_code("if True\n    pass\n")
    assert len(result.syntax_findings) == 1
    assert result.ruff_skipped is True
    assert result.complexity_skipped is True
    assert result.ruff_findings == []
    assert result.error_count == 1


def test_mixed_findings_are_counted():
    result = review_code("import os\n\n\ndef f(x):\n    return y\n")
    assert result.error_count == 1    # F821 undefined name
    assert result.warning_count == 1  # F401 unused import
    assert result.style_count == 0
    assert result.flagged_function_count == 0


def test_ruff_failure_does_not_hide_radon(monkeypatch):
    monkeypatch.setattr(pipeline, "run_ruff", lambda code: ([], "boom"))
    result = review_code("def f():\n    return 1\n")
    assert result.ruff_error == "boom"
    assert len(result.complexity) == 1


def test_review_records_time():
    assert review_code("x = 1\n").seconds >= 0