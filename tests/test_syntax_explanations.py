from pathlib import Path

import pytest

from analyzers.syntax_check import _EXPLANATIONS, _GENERIC_EXPLANATION, check_syntax

DATA = Path(__file__).resolve().parent.parent / "eval_data" / "generated"

# The vaguest template: used when no more specific one matches.
_CATCH_ALL = next(
    (explanation, suggestion)
    for needle, explanation, suggestion in _EXPLANATIONS
    if needle == "invalid syntax"
)


@pytest.mark.parametrize(
    "path", sorted(DATA.glob("syntax_*.py")), ids=lambda p: p.name
)
def test_syntax_error_gets_a_specific_explanation(path):
    findings = check_syntax(path.read_bytes().decode("utf-8"))
    assert len(findings) == 1
    finding = findings[0]
    pair = (finding.explanation, finding.suggestion)
    assert pair != _GENERIC_EXPLANATION, f"generic text for: {finding.message}"
    assert pair != _CATCH_ALL, f"only the catch-all text for: {finding.message}"