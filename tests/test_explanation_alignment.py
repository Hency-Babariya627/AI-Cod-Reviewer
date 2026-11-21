from pathlib import Path

import pytest

from analyzers.ruff_check import _EXPLANATIONS
from pipeline import review_code

DATA = Path(__file__).resolve().parent.parent / "eval_data" / "generated"


def _sample_files(per_rule: int = 2):
    """First `per_rule` single-rule files for each rule, e.g. single_e713_01.py."""
    chosen, seen = [], {}
    for path in sorted(DATA.glob("single_*.py")):
        rule = path.stem.split("_")[1].upper()
        if seen.get(rule, 0) < per_rule:
            seen[rule] = seen.get(rule, 0) + 1
            chosen.append((rule, path))
    return chosen


@pytest.mark.parametrize("rule,path", _sample_files(), ids=lambda v: getattr(v, "name", v))
def test_explanation_matches_the_reported_rule(rule, path):
    result = review_code(path.read_bytes().decode("utf-8"))
    findings = [f for f in result.ruff_findings if f.rule == rule]
    assert findings, f"{path.name}: expected a {rule} finding"
    for finding in result.ruff_findings:
        assert finding.rule in _EXPLANATIONS, f"{finding.rule} fell back to the generic text"
        explanation, suggestion = _EXPLANATIONS[finding.rule]
        assert finding.explanation == explanation
        assert finding.suggestion.startswith(suggestion)