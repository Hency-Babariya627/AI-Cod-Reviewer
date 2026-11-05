import warnings

from models import Finding

# (text to look for in Python's message, explanation, suggestion)
# Order matters: the first match wins, so specific entries come first.
_EXPLANATIONS = [
    (
        "was never closed",
        "A bracket, parenthesis, or brace was opened but never closed.",
        "Look at the reported line, find the opening symbol, and add the matching closing one.",
    ),
    (
        "unterminated string literal",
        "A piece of text (a string) started with a quote but the closing quote is missing.",
        "Add the matching closing quote at the end of the text.",
    ),
    (
        "expected ':'",
        "Statements like if, for, while, def, and class must end with a colon.",
        "Add a ':' at the end of the reported line.",
    ),
    (
        "expected an indented block",
        "After a line ending in ':' Python expects the next line to be indented.",
        "Indent the line(s) after the colon, usually by 4 spaces.",
    ),
    (
        "unexpected indent",
        "This line is indented more than the code around it, and Python doesn't know why.",
        "Remove the extra spaces so the line lines up with the code above it.",
    ),
    (
        "unindent does not match",
        "The indentation of this line doesn't line up with any earlier block.",
        "Make the spacing match the block you want this line to belong to. Use 4 spaces consistently.",
    ),
    (
        "Missing parentheses in call to 'print'",
        "In Python 3, print is a function, so it needs parentheses.",
        "Write print(...) instead of print ...",
    ),
    (
        "Perhaps you forgot a comma",
        "Python found two values next to each other with nothing between them.",
        "Check for a missing comma in the list, tuple, or function call.",
    ),
    (
        "Maybe you meant '=='",
        "A single '=' stores a value in a variable. Comparing two values uses '=='.",
        "Use '==' if you meant to compare, for example: if x == 5:",
    ),
    (
        "outside function",
        "'return' can only be used inside a function (a block that starts with def).",
        "Put this line inside a function, or remove it.",
    ),
    (
        "invalid syntax",
        "Python could not understand this line. The problem is often on this line or just before it.",
        "Check this line and the one above it for missing colons, brackets, quotes, or commas.",
    ),
]

_GENERIC_EXPLANATION = (
    "Python could not understand the structure of this code.",
    "Read the message and the highlighted line carefully. The mistake is often on this line or the line before.",
)


def _explain(message: str) -> tuple[str, str]:
    for needle, explanation, suggestion in _EXPLANATIONS:
        if needle in message:
            return explanation, suggestion
    return _GENERIC_EXPLANATION


def check_syntax(code: str) -> list[Finding]:
    """Check Python syntax WITHOUT running the code.

    compile() only parses the text and builds code that is never executed.
    Returns an empty list if the syntax is valid.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # hide SyntaxWarnings; Ruff reports those later
            compile(code, "<submitted>", "exec", dont_inherit=True)
    except SyntaxError as err:  # IndentationError and TabError are subclasses
        explanation, suggestion = _explain(err.msg or "")
        return [
            Finding(
                source="syntax",
                rule=type(err).__name__,
                message=err.msg or "Invalid syntax",
                severity="error",
                line=err.lineno,
                column=err.offset,
                explanation=explanation,
                suggestion=suggestion,
            )
        ]
    except (ValueError, RecursionError, MemoryError) as err:
        # Examples: null bytes in the text, or code nested too deeply to parse.
        return [
            Finding(
                source="syntax",
                rule="CheckFailed",
                message=str(err) or type(err).__name__,
                severity="error",
                explanation="The syntax checker could not process this code.",
                suggestion="Check for unusual characters or extremely deep nesting.",
            )
        ]
    return []