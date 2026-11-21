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
        "A variable is given a value but never used afterwards.",
        "Delete the line, or use the variable, for example return it or print it. If the right-hand side is a function call you still need, keep the call and drop the 'name =' part.",
    ),
    "F811": (
        "The same name is defined twice, for example two functions called 'greet', and the first one is never used before the second replaces it. Python only keeps the last one.",
        "If you need both, give them different names and update every place that calls the one you renamed. If you only need one, delete the other.",
    
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
        "This line is longer than 88 characters (Ruff's default limit), which makes code harder to read.",
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
        "Use 'is None' or 'is not None'. Example: 'if x == None:' becomes 'if x is None:'.",
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
        "Use 'def name(...):' instead. Example: 'double = lambda x: x * 2' becomes 'def double(x):' followed by an indented 'return x * 2'.",
    ),
    "E741": (
        "A variable is named 'l', 'O', or 'I', which look like the numbers 1 and 0.",
        "Rename it to something descriptive, for example 'length', 'line' or 'index' instead of 'l'.",
    ),
    "W291": (
        "There are extra spaces at the end of this line.",
        "Delete the trailing spaces. Most editors can do this automatically.",
    ),
    "W292": (
        "The last line of the file does not end with a newline character.",
        "Press Enter once at the end of the file, so the last line ends properly.",
    ),
    "W293": (
        "A blank line contains spaces or tabs.",
        "Delete the spaces so the line is truly empty.",
    ),
    "W605": (
        "A backslash in a normal string is not a valid escape sequence (such as \\d).",
        "Put an 'r' before the string, like r'\\d', or double the backslash.",
    ),
    "E713": (
        "A membership test is written as 'not x in y'. It works, but it is easy to misread.",
        "Write 'x not in y' instead. Example: 'if not a in items:' becomes 'if a not in items:'.",
    ),
    "E714": (
        "An identity test is written as 'not x is y'. It works, but it is easy to misread.",
        "Write 'x is not y' instead. Example: 'if not a is b:' becomes 'if a is not b:'.",
    ),
    "E721": (
        "The code checks a type with '==', for example 'type(value) == int'. This only matches the exact type and fails for types built on it.",
        "Replace it with 'isinstance(value, int)', where 'int' is the type you are checking for.",
    ),
    "F632": (
        "'is' or 'is not' is used to compare with a text or number. 'is' asks whether both sides are the very same object, not whether the values are equal, so the result can be wrong.",
        "Use '==' or '!=' to compare values. Keep 'is' for None. Example: 'if age is 18:' becomes 'if age == 18:'.",
    ),
    "W191": (
        "This line is indented with a tab instead of spaces.",
        "Use 4 spaces for each level of indentation. Most editors can convert tabs to spaces.",
    ),
    "F403": (
        "'from module import *' brings in every name from a module, so it is unclear where a name comes from.",
        "Import only what you need, for example 'from math import sqrt', or use 'import math'.",
    ),
    "F405": (
        "This name was probably imported by 'from module import *', so Ruff cannot check that it exists. A star import hides where names come from.",
        "List the names you use, for example 'from math import sqrt', instead of 'from math import *'.",
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