from pipeline import review_code


def test_valid_code_gets_an_overview():
    result = review_code("def add(a, b):\n    return a + b\n")
    assert result.overview_error is None
    assert [f.name for f in result.overview.functions] == ["add"]


def test_syntax_error_skips_the_overview():
    result = review_code("if True\n    pass\n")
    assert result.overview is None and result.overview_error is None
    assert len(result.syntax_findings) == 1


def test_empty_code_gives_an_empty_overview():
    result = review_code("")
    assert result.overview is not None and result.overview.functions == []