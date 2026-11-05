# Design Decisions (Sprint 1)

## Architecture

Input (Streamlit) -> `review_code()` in `pipeline.py` -> syntax check ->
Ruff -> Radon -> `ReviewResult` -> displayed by `app.py`.

Each analyzer is a separate module with no UI code, so it can be tested
independently of Streamlit. `app.py` only handles input and display.

## Key decisions

| Decision | Reason |
|---|---|
| Never execute submitted code | Untrusted input. `compile()`, Ruff (stdin), and Radon only parse text. Tests confirm a file-writing snippet does not run. |
| `compile()` for syntax, not `ast.parse` | Also catches errors such as `return` outside a function. |
| Ruff as a subprocess with `--isolated`, `--no-cache`, stdin | Ignores machine-specific config so results are repeatable; nothing is written to disk. |
| Ruff rules `E,F,W` | Pyflakes and pycodestyle cover unused imports, undefined names, and style. Complexity is left to Radon. |
| Severity: error / warning / info | Distinguishes likely bugs (undefined names), probable mistakes (unused imports), and style advice. |
| Radon via Python API | Parses text only and avoids process start-up cost. |
| Complexity flagged at score 6+ (Radon rank B) | Radon's convention, not a universal rule. Shown with a caveat in the UI. |
| Tools return `(results, error)` | A failed tool is never displayed as "no issues". |
| Ruff and Radon skipped on syntax errors | Results on unparseable code can be incomplete or misleading. |
| Analyzers run once per click; result stored with its code | Prevents stale results: if the editor text differs from `result.code`, a warning replaces the results. |
| Common `Finding` format | Preserves source, rule, location, message, severity, explanation, suggestion. |

## Measured finding: Ruff start-up time

On the development machine (Windows 11, Python 3.13.9, Ruff 0.17.3):

- `python -m ruff --version`: 2.14 s. Calling `ruff.exe` directly: 0.049 s.
- Switching to the executable cut the full test suite from 19.2 s to 2.07 s.

These are single-machine measurements, not formal benchmarks. Formal runtime
evaluation is planned for Sprint 4.

## Test status

36 automated tests passed (syntax, Ruff, Radon, pipeline) at the time of writing.
Browser behaviour (upload, edit, clear, stale results) was checked manually.