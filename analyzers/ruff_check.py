import json
import shutil
import subprocess
import sys
from pathlib import Path

from models import Finding

RUFF_TIMEOUT_SECONDS = 15
SELECTED_RULES = "E,F,W"

# Rule prefixes that usually mean a real bug (undefined names, syntax-level problems).
_ERROR_PREFIXES = ("E9", "F63", "F7", "F82")

# rule code -> (what it means, how to fix it)
_EXPLANATIONS = {
    "F401": (
        "An import brings in a module or name that your code never uses.",
        "Remove the unused import, or use it. Unused imports clutter the file.",
    ),
    "F821": (
        "The code uses a name that was never defined. Python will stop with a NameError when this line runs.",
        "Check for a typo, or define the variable, function, or import before using it.",
    ),
    "F841": (
        "A variable was given a value but is never used afterwards.",
        "Remove the variable, or use its value. If you only need the function call, drop the 'name =' part.",
    ),
    "F811": (
        "A name is defined again before the first definition was used, so the first one is lost.",
        "Rename one of them, or delete the one you do not need.",
    ),
    "F541": (
        "This f-string has no {placeholders}, so the 'f' in front does nothing.",
        "Remove the 'f' prefix, or add a {value} inside the text.",
    ),
    "E401": (
        "Several modules are imported on one line.",
        "Put each import on its own line.",
    ),
    "E402": (
        "An import appears after other code. Imports are normally at the top of the file.",
        "Move the import to the top of the file.",
    ),
    "E501": (
        "This line is very long, which makes code harder to read.",
        "Split it over several lines or shorten it. This is a style recommendation, not a bug.",
    ),
    "E701": (
        "Two statements are on one line (for example 'if x: do()').",
        "Put the second statement on its own indented line.",
    ),
    "E702": (
        "Two statements are on one line, separated by a semicolon.",
        "Put each statement on its own line.",
    ),
    "E703": (
        "A semicolon at the end of a line is not needed in Python.",
        "Remove the semicolon.",
    ),
    "E711": (
        "Comparing to None with '==' or '!=' can behave unexpectedly.",
        "Use 'is None' or 'is not None'.",
    ),
    "E712": (
        "Comparing to True or False with '==' is unnecessary.",
        "Write 'if x:' instead of 'if x == True:', and 'if not x:' for False.",
    ),
    "E722": (
        "A bare 'except:' catches every error, even ones you did not expect, which can hide bugs.",
        "Catch a specific error such as 'except ValueError:', or use 'except Exception:'.",
    ),
    "E731": (
        "A lambda was assigned to a name. A normal function is clearer.",
        "Use 'def name(...):' instead.",
    ),
    "E741": (
        "A variable is named 'l', 'O', or 'I', which look like the numbers 1 and 0.",
        "Use a more descriptive name.",
    ),
    "W291": (
        "There are extra spaces at the end of this line.",
        "Delete the trailing spaces. Most editors can do this automatically.",
    ),
    "W292": (
        "The file does not end with a blank line.",
        "Press Enter once at the end of the file.",
    ),
    "W293": (
        "A blank line contains spaces or tabs.",
        "Delete the spaces so the line is truly empty.",
    ),
    "W605": (
        "A backslash in a normal string is not a valid escape sequence (such as \\d).",
        "Put an 'r' before the string, like r'\\d', or double the backslash.",
    ),
}

_GENERIC = (
    "Ruff flagged this line under this rule.",
    "Search the rule code in the Ruff rules documentation (docs.astral.sh/ruff/rules) to learn more.",
)


def _severity(code: str) -> str:
    if code.startswith(_ERROR_PREFIXES):
        return "error"
    if code.startswith("F"):
        return "warning"
    return "info"  # E and W rules that are not in the error list are style advice

def _ruff_base_command() -> list[str]:
    """Prefer the ruff executable in the active environment (much faster to start).

    Falls back to 'python -m ruff' if the executable cannot be found.
    """
    scripts_dir = Path(sys.executable).parent
    exe = shutil.which("ruff", path=str(scripts_dir))
    if exe:
        return [exe]
    return [sys.executable, "-m", "ruff"]

def run_ruff(code: str) -> tuple[list[Finding], str | None]:
    """Run Ruff on the code text WITHOUT executing it.

    Returns (findings, error_message). error_message is None when Ruff ran
    successfully, even if it found nothing. If it is not None, Ruff failed and
    the findings list should not be trusted.
    """
    command = [
        *_ruff_base_command(), "check",
        "--isolated",
        "--no-cache",
        "--select", SELECTED_RULES,
        "--output-format", "json",
        "--stdin-filename", "submitted.py",
        "-",
    ]
    try:
        result = subprocess.run(
            command,
            input=code,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=RUFF_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return [], f"Ruff took longer than {RUFF_TIMEOUT_SECONDS} seconds and was stopped."
    except (OSError, ValueError) as err:
        return [], f"Ruff could not be started: {err}"

    # Ruff exit codes: 0 = no issues, 1 = issues found, 2 = Ruff itself failed.
    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError:
        detail = (result.stderr or result.stdout).strip()[:300]
        return [], f"Ruff returned output we could not read. {detail}"
    if result.returncode not in (0, 1) or not isinstance(items, list):
        detail = result.stderr.strip()[:300]
        return [], f"Ruff failed (exit code {result.returncode}). {detail}"

    findings = []
    for item in items:
        code_id = item.get("code") or "RuffError"  # syntax errors have no rule code
        location = item.get("location") or {}
        explanation, suggestion = _EXPLANATIONS.get(code_id, _GENERIC)
        if item.get("fix"):
            suggestion += " Ruff can fix this automatically."
        findings.append(
            Finding(
                source="ruff",
                rule=code_id,
                message=item.get("message", ""),
                severity=_severity(code_id),
                line=location.get("row"),
                column=location.get("column"),
                explanation=explanation,
                suggestion=suggestion,
            )
        )

    findings.sort(key=lambda f: (f.line or 0, f.column or 0))
    return findings, None