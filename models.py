from dataclasses import dataclass


@dataclass
class Finding:
    """One problem found in the submitted code, from any analyzer."""

    source: str                  # which tool found it: "syntax", "ruff", "radon"
    rule: str                    # e.g. "SyntaxError", later "F401"
    message: str                 # the technical message from the tool
    severity: str                # "error", "warning", or "info"
    line: int | None = None      # line number, if known
    column: int | None = None    # column number, if known
    explanation: str = ""        # beginner-friendly "what and why"
    suggestion: str = ""         # beginner-friendly "how to fix"