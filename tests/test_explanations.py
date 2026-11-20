import pytest

from analyzers.ruff_check import _EXPLANATIONS, _GENERIC, run_ruff

# The 25 rules covered by the evaluation set, plus star-import rules
# that beginners meet often.
REPORTABLE_RULES = [
    "E401", "E402", "E501", "E701", "E702", "E703", "E711", "E712",
    "E713", "E714", "E721", "E722", "E731", "E741",
    "F401", "F541", "F632", "F811", "F821", "F841",
    "W191", "W291", "W292", "W293", "W605",
    "F403", "F405",
]


@pytest.mark.parametrize("rule", REPORTABLE_RULES)
def test_rule_has_its_own_explanation(rule):
    assert rule in _EXPLANATIONS, f"{rule} would show the generic text"


@pytest.mark.parametrize("rule", sorted(_EXPLANATIONS))
def test_explanation_is_complete(rule):
    explanation, suggestion = _EXPLANATIONS[rule]
    assert explanation.strip() and suggestion.strip()
    assert (explanation, suggestion) != _GENERIC


def test_new_template_reaches_the_user():
    findings, error = run_ruff("items = [1]\nif not 1 in items:\n    pass\n")
    assert error is None
    match = [f for f in findings if f.rule == "E713"]
    assert match, "Ruff did not report E713"
    assert match[0].explanation == _EXPLANATIONS["E713"][0]