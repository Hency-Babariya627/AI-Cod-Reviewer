# Design Decisions

Last updated 21 November 2026 (Sprint 3).

## Architecture

Input (Streamlit) -> `review_code()` in `pipeline.py` -> syntax check ->
Ruff + Radon + `ast` overview -> `ReviewResult` -> displayed by `app.py`.

- Each analyzer is a separate module with no UI code, so it can be tested without Streamlit:
  `analyzers/syntax_check.py`, `analyzers/ruff_check.py`, `analyzers/radon_check.py`,
  `overview.py`, `findings.py`.
- `app.py` only handles input and display. `styles.py` holds the CSS and fixed HTML.
- The result of one review is stored together with the exact code it was run on.

## Key decisions

| Decision | Reason |
|---|---|
| Never execute submitted code | Untrusted input. `compile()`, Ruff (stdin), Radon and `ast.parse` only read text. One test per analyzer submits code that would create a file if it ran and checks that no file appears. |
| `compile()` for syntax, not `ast.parse` | Also catches errors such as `return` outside a function. |
| Ruff as a subprocess with `--isolated`, `--no-cache`, stdin | Ignores machine-specific config so results are repeatable; nothing is written to disk. |
| Call the `ruff` executable directly | Starting it through `python -m ruff` was about 40 times slower on the development machine (see measurement below). |
| Ruff rules `E,F,W` | Pyflakes and pycodestyle cover unused imports, undefined names and style. Complexity is left to Radon. |
| Severity: error / warning / info | Separates likely bugs (undefined names), probable mistakes (unused imports) and style advice. |
| Radon through its Python API | Parses text only and avoids process start-up cost. |
| Complexity flagged at score 6 or higher (Radon rank B) | Radon's convention, not a universal rule. The interface says so. |
| Tools return `(results, error)` | A failed tool is never shown as "no issues". |
| Ruff, Radon and the overview are skipped on syntax errors | Results on unparseable code can be incomplete or misleading. |
| Analyzers run once per click; the result stores its code | Prevents stale results: if the editor text differs from `result.code`, a warning replaces the results. |
| Common `Finding` format | Keeps source, rule, location, message, severity, explanation and suggestion together. |
| Overview built with `ast`, structure only | Needs no AI service. It lists imports, functions, classes and what runs, and says plainly that it cannot judge correctness. Its "uses" notes follow only functions defined in the same file. |
| Findings table in `findings.py` | One list of syntax, Ruff and flagged Radon findings, sorted by severity then line. A flagged function becomes a row with severity "info" because it is a hint, not an error. |
| Severity and Source filters | Severity is not enough: a Radon row would otherwise be hidden under "Style / info". |
| CSV cells that start with `=`, `+`, `-` or `@` get a leading quote | Stops spreadsheet programs from running submitted text as a formula. |
| Markdown tables instead of `st.dataframe` | Windows Application Control blocked `pyarrow` on the development machine, which `st.dataframe` needs. |
| Both pages ("Code Reviewer", "About") are tabs | Streamlit drops the state of widgets that are not drawn on a run, so a page switch would have erased the editor text. |
| Uploader handled before the text area is created | An upload fills the editor through session state, which can only be set before the widget exists. Containers keep the on-screen order. |
| Repeated Ruff findings grouped by rule | Ten long-line warnings become one entry instead of ten. |
| HTML in `styles.py` is fixed text; submitted text is escaped | Nothing from the submitted code is rendered as HTML, and Markdown characters in docstrings and defaults are escaped or shown inside code spans. |
| Upload limit 200 KB in the app, 1 MB in Streamlit's config | The app gives a friendly error for files between the two. |
| Explanations are rule-based templates in `ruff_check.py` and `syntax_check.py`, with a generic fallback | Works without an AI service and can be tested. A test fails if a rule in the evaluation set has no template. |
| Explanation quality checked with a 1 to 3 rubric by two raters, then rewritten and rated again | Follows the proposal's rubric (accuracy, clarity, actionability, unsupported claims). Unchanged controls were included to show rater noise. |
| Evaluation labels come from the edit made to each file, not from tool output | A label copied from the tool would make the score circular. Ruff was used only afterwards to catch design mistakes. |

## Measured finding: Ruff start-up time

On the development machine (Windows 11, Python 3.13.9, Ruff 0.17.3):

- `python -m ruff --version`: 2.14 s. Calling `ruff.exe` directly: 0.049 s.
- Switching to the executable cut the test suite from 19.2 s to 2.07 s at the time.

These are single-machine measurements, not formal benchmarks. Formal runtime
evaluation is planned for Sprint 4.

## Test status

203 automated tests pass (syntax, Ruff, Radon, pipeline, findings, overview, explanation
coverage, explanation alignment with the real findings, and syntax-error explanations).
Browser behaviour was checked manually.

The labelled evaluation (452 files, `python evaluate.py`) reported all 362 expected findings
with no extra findings, matched all 18 expected complexity flags, detected all 28 syntax
errors and gave no findings on 109 clean files. These scores show that the integration is
correct; they do not show general accuracy, because the data is short and only
covers rules Ruff supports. Explanation quality was rated for 10 rules by two raters;
see `docs/explanation_ratings/`.