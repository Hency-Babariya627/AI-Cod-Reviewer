from types import SimpleNamespace as NS

from findings import collect_rows, filter_rows, to_csv, to_markdown_table


def finding(source, rule, severity, line, message="msg"):
    return NS(source=source, rule=rule, severity=severity, line=line, column=1,
              message=message, explanation="why", suggestion="fix")


def complexity(name, line, score, rank, flagged):
    return NS(name=name, line=line, complexity=score, rank=rank, flagged=flagged,
              explanation="why", suggestion="fix")


def result(syntax=(), ruff=(), cx=()):
    return NS(syntax_findings=list(syntax), ruff_findings=list(ruff), complexity=list(cx))


def test_empty_result_has_no_rows():
    assert collect_rows(result()) == []


def test_rows_sorted_errors_first_then_by_line():
    r = result(ruff=[finding("ruff", "E501", "info", 1),
                     finding("ruff", "F401", "warning", 5),
                     finding("ruff", "F821", "error", 9)])
    assert [x["rule"] for x in collect_rows(r)] == ["F821", "F401", "E501"]


def test_only_flagged_functions_become_radon_rows():
    r = result(cx=[complexity("easy", 1, 1, "A", False), complexity("hard", 10, 12, "C", True)])
    rows = collect_rows(r)
    assert len(rows) == 1
    assert rows[0]["source"] == "radon" and rows[0]["rule"] == "CC-C"
    assert "hard" in rows[0]["message"] and rows[0]["severity"] == "info"


def test_syntax_finding_is_included():
    r = result(syntax=[finding("syntax", "SyntaxError", "error", 2, "expected ':'")])
    assert collect_rows(r)[0]["rule"] == "SyntaxError"


def test_filter_by_severity():
    rows = collect_rows(result(ruff=[finding("ruff", "E501", "info", 1), finding("ruff", "F821", "error", 2)]))
    assert [x["rule"] for x in filter_rows(rows, ["error"])] == ["F821"]
    assert filter_rows(rows, []) == []


def test_csv_has_header_and_one_line_per_row():
    rows = collect_rows(result(ruff=[finding("ruff", "F401", "warning", 1, "`os` imported but unused")]))
    lines = to_csv(rows).strip().split("\n")
    assert lines[0].startswith("Source,Rule,Severity,Line,Message")
    assert len(lines) == 2 and "F401" in lines[1] and "Warning" in lines[1]


def test_csv_blocks_formula_injection():
    rows = collect_rows(result(ruff=[finding("ruff", "F821", "error", 1, "=HYPERLINK(\"http://x\")")]))
    assert "'=HYPERLINK" in to_csv(rows)


def test_csv_keeps_commas_and_quotes_intact():
    import csv, io
    rows = collect_rows(result(ruff=[finding("ruff", "F821", "error", 1, 'a, "b" c')]))
    parsed = list(csv.reader(io.StringIO(to_csv(rows))))
    assert parsed[1][4] == 'a, "b" c'


def test_markdown_table_escapes_pipes_and_newlines():
    rows = collect_rows(result(ruff=[finding("ruff", "F821", "error", 1, "a | b\nc")]))
    table = to_markdown_table(rows)
    assert "a \\| b c" in table
    assert len(table.split("\n")) == 3  # header, separator, one row


def test_missing_line_number_is_blank_not_a_crash():
    rows = collect_rows(result(syntax=[finding("syntax", "CheckFailed", "error", None)]))
    assert "None" not in to_markdown_table(rows) and to_csv(rows).count("None") == 0


def test_filter_by_source():
    rows = collect_rows(result(
        ruff=[finding("ruff", "E501", "info", 1)],
        cx=[complexity("hard", 5, 12, "C", True)],
    ))
    only_radon = filter_rows(rows, ["error", "warning", "info"], ["radon"])
    assert [x["source"] for x in only_radon] == ["radon"]
    assert filter_rows(rows, ["error", "warning", "info"], []) == []
    assert len(filter_rows(rows, ["error", "warning", "info"])) == 2  # no source filter given


def test_source_and_severity_filters_combine():
    rows = collect_rows(result(
        ruff=[finding("ruff", "F821", "error", 2), finding("ruff", "E501", "info", 1)],
        cx=[complexity("hard", 5, 12, "C", True)],
    ))
    shown = filter_rows(rows, ["info"], ["ruff"])
    assert [x["rule"] for x in shown] == ["E501"]