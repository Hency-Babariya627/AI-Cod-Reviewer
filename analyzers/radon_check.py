from dataclasses import dataclass

from radon.complexity import cc_rank, cc_visit

# Radon's convention: rank A is 1-5, B is 6-10, C is 11-20, and so on.
# We flag B and above, i.e. a score of 6 or more.
FLAG_THRESHOLD = 6

_RANK_MEANING = {
    "A": "simple",
    "B": "moderately complex",
    "C": "complex",
    "D": "very complex",
    "E": "extremely complex",
    "F": "extremely complex",
}


@dataclass
class ComplexityResult:
    """Complexity of one function or method."""

    name: str
    line: int
    complexity: int
    rank: str          # "A" to "F"
    flagged: bool      # True if complexity >= FLAG_THRESHOLD
    explanation: str
    suggestion: str


def _describe(name: str, score: int, rank: str) -> tuple[str, str]:
    meaning = _RANK_MEANING.get(rank, "complex")
    explanation = (
        f"'{name}' has a complexity score of {score} (rank {rank}, {meaning}). "
        "The score is roughly the number of different paths the code can take: "
        "each if, loop, except, and 'and'/'or' adds one. More paths mean more "
        "cases to test and understand. This is a guide, not a verdict. "
        "Some code is naturally branchy and still clear."
    )
    if score < FLAG_THRESHOLD:
        suggestion = "No action needed."
    else:
        suggestion = (
            "Ideas to simplify: move a chunk of the work into a smaller helper "
            "function with a clear name; replace deeply nested ifs with early "
            "'return' statements; or replace a long if/elif chain with a "
            "dictionary lookup. Only change it if it is hard to read or test."
        )
    return explanation, suggestion


def analyze_complexity(code: str) -> tuple[list[ComplexityResult], str | None]:
    """Measure cyclomatic complexity WITHOUT running the code.

    Returns (results, error_message). error_message is None on success, even
    if there are no functions. Results are sorted with the most complex first.
    """
    try:
        blocks = cc_visit(code)
    except SyntaxError as err:
        return [], f"The code could not be parsed for complexity analysis: {err.msg}"
    except Exception as err:  # keep the app alive if Radon fails unexpectedly
        return [], f"Radon failed: {type(err).__name__}: {err}"

    results = []
    for block in blocks:
        # Methods have a classname; show them as Class.method. Skip class summaries.
        if not hasattr(block, "classname") and hasattr(block, "methods"):
            continue
        name = block.name
        classname = getattr(block, "classname", None)
        if classname:
            name = f"{classname}.{block.name}"
        score = block.complexity
        rank = cc_rank(score)
        explanation, suggestion = _describe(name, score, rank)
        results.append(
            ComplexityResult(
                name=name,
                line=block.lineno,
                complexity=score,
                rank=rank,
                flagged=score >= FLAG_THRESHOLD,
                explanation=explanation,
                suggestion=suggestion,
            )
        )

    results.sort(key=lambda r: (-r.complexity, r.line))
    return results, None