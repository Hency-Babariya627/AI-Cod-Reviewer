from analyzers.syntax_check import check_syntax


def test_valid_code_has_no_findings():
    assert check_syntax("x = 1\nprint(x)\n") == []


def test_empty_code_has_no_findings():
    assert check_syntax("") == []


def test_missing_colon_reports_line_2():
    findings = check_syntax("x = 1\nif x == 1\n    print(x)\n")
    assert len(findings) == 1
    assert findings[0].line == 2
    assert findings[0].explanation != ""


def test_unclosed_parenthesis_reports_line_1():
    findings = check_syntax("print('hi'\n")
    assert len(findings) == 1
    assert findings[0].line == 1


def test_unterminated_string_reports_line_1():
    findings = check_syntax("name = 'Ana\nprint(name)\n")
    assert len(findings) == 1
    assert findings[0].line == 1


def test_missing_indent_is_indentation_error():
    findings = check_syntax("def f():\nprint(1)\n")
    assert len(findings) == 1
    assert findings[0].rule == "IndentationError"


def test_unexpected_indent_reports_line_2():
    findings = check_syntax("x = 1\n    y = 2\n")
    assert len(findings) == 1
    assert findings[0].rule == "IndentationError"
    assert findings[0].line == 2


def test_return_outside_function_is_caught():
    findings = check_syntax("return 5\n")
    assert len(findings) == 1


def test_null_byte_does_not_crash():
    findings = check_syntax("x = 1\0\n")
    assert len(findings) == 1


def test_code_is_never_executed(tmp_path):
    marker = tmp_path / "marker.txt"
    code = f"open({str(marker)!r}, 'w').write('ran')\n"
    assert check_syntax(code) == []
    assert not marker.exists()  # if the code had run, this file would exist