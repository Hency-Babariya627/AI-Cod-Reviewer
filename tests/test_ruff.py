import subprocess

from analyzers import ruff_check
from analyzers.ruff_check import run_ruff


def test_clean_code_has_no_findings():
    findings, error = run_ruff("import os\nprint(os.getcwd())\n")
    assert error is None
    assert findings == []


def test_empty_code_has_no_findings():
    findings, error = run_ruff("")
    assert error is None
    assert findings == []


def test_unused_import_is_warning():
    findings, error = run_ruff("import os\n")
    assert error is None
    assert len(findings) == 1
    assert findings[0].rule == "F401"
    assert findings[0].line == 1
    assert findings[0].severity == "warning"
    assert findings[0].explanation != ""


def test_undefined_name_is_error():
    findings, error = run_ruff("print(total)\n")
    assert error is None
    assert [f.rule for f in findings] == ["F821"]
    assert findings[0].severity == "error"


def test_unused_variable_is_found():
    findings, _ = run_ruff("def f():\n    unused = 1\n")
    assert "F841" in [f.rule for f in findings]


def test_long_line_is_style_info():
    findings, _ = run_ruff("x = '" + "a" * 100 + "'\n")
    assert [f.rule for f in findings] == ["E501"]
    assert findings[0].severity == "info"


def test_trailing_whitespace_is_style_info():
    findings, _ = run_ruff("x = 1   \n")
    assert [f.rule for f in findings] == ["W291"]
    assert findings[0].severity == "info"


def test_findings_are_sorted_by_line():
    findings, _ = run_ruff("import os\nimport sys\nprint(x)\n")
    assert [f.line for f in findings] == [1, 2, 3]


def test_missing_tool_is_reported_not_hidden(monkeypatch):
    def fail(*args, **kwargs):
        raise FileNotFoundError("ruff not found")

    monkeypatch.setattr(ruff_check.subprocess, "run", fail)
    findings, error = run_ruff("x = 1\n")
    assert findings == []
    assert error is not None


def test_timeout_is_reported(monkeypatch):
    def slow(*args, **kwargs):
        raise subprocess.TimeoutExpired("ruff", 15)

    monkeypatch.setattr(ruff_check.subprocess, "run", slow)
    findings, error = run_ruff("x = 1\n")
    assert findings == []
    assert "seconds" in error


def test_code_is_never_executed(tmp_path):
    marker = tmp_path / "marker.txt"
    code = f"open({str(marker)!r}, 'w').write('ran')\n"
    run_ruff(code)
    assert not marker.exists()