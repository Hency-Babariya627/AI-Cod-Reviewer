import json
import urllib.error

import pytest

import llm_explain
from llm_explain import MAX_ANSWER_CHARS, MAX_LINE_CHARS, OllamaProvider, enhance_explanation, line_of
from models import Finding

CODE = "import os\nsecret_token = 'abc123'\nl = 1\n"


def make_finding(line=3):
    return Finding(
        source="ruff", rule="E741", message="Ambiguous variable name: `l`",
        severity="info", line=line, column=1,
        explanation="A variable is named 'l'.", suggestion="Use a more descriptive name.",
    )


def test_returns_the_model_answer_cleaned_up():
    fake = lambda prompt: "  A friendlier   explanation. \n"
    assert enhance_explanation(make_finding(), CODE, fake) == "A friendlier explanation."


def test_only_the_flagged_line_is_sent():
    prompts = []
    enhance_explanation(make_finding(), CODE, lambda p: prompts.append(p) or "ok")
    assert "l = 1" in prompts[0]
    assert "secret_token" not in prompts[0]
    assert "import os" not in prompts[0]


def test_missing_line_number_still_works():
    assert enhance_explanation(make_finding(line=None), CODE, lambda p: "ok") == "ok"


def test_long_line_is_cut():
    assert len(line_of("x = " + "a" * 500, 1)) == MAX_LINE_CHARS


def test_line_out_of_range_is_empty():
    assert line_of(CODE, 99) == ""


@pytest.mark.parametrize("answer", ["", "   \n ", None])
def test_empty_or_wrong_type_answer_falls_back(answer):
    assert enhance_explanation(make_finding(), CODE, lambda p: answer) is None


@pytest.mark.parametrize(
    "error",
    [OSError("down"), TimeoutError(), urllib.error.URLError("refused"),
     ValueError("bad json"), KeyError("response")],
)
def test_model_failures_fall_back(error):
    def broken(prompt):
        raise error
    assert enhance_explanation(make_finding(), CODE, broken) is None


def test_very_long_answer_is_shortened():
    result = enhance_explanation(make_finding(), CODE, lambda p: "word " * 1000)
    assert len(result) <= MAX_ANSWER_CHARS


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com"])
def test_only_http_addresses_are_allowed(url):
    with pytest.raises(ValueError):
        OllamaProvider(base_url=url)


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_ollama_provider_reads_the_response_field(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["timeout"] = timeout
        seen["body"] = json.loads(request.data)
        return FakeResponse(json.dumps({"response": "Hi there"}).encode("utf-8"))

    monkeypatch.setattr(llm_explain.urllib.request, "urlopen", fake_urlopen)
    provider = OllamaProvider(model="m", base_url="http://localhost:11434/", timeout=5)
    assert provider("hello") == "Hi there"
    assert seen["url"] == "http://localhost:11434/api/generate"
    assert seen["timeout"] == 5
    assert seen["body"]["model"] == "m"
    assert seen["body"]["stream"] is False