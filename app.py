import streamlit as st

from findings import (
    SEVERITY_LABELS,
    SOURCE_LABELS,
    collect_rows,
    filter_rows,
    to_csv,
    to_markdown_table,
)
from overview import escape_markdown
from pipeline import review_code
from styles import (
    APP_NAME,
    CSS,
    EMPTY_STATE_HTML,
    FOOTER_HTML,
    HERO_HTML,
    MODULE_CARDS_HTML,
    SIDEBAR_HTML,
    section_html,
)

MAX_FILE_SIZE = 200 * 1024  # 200 KB limit for uploaded files
MAX_OCCURRENCES_SHOWN = 8   # per Ruff rule, so long lists stay readable
MAX_TABLE_ROWS = 200        # rows shown in the findings table; the CSV has them all
MAX_OVERVIEW_ITEMS = 40     # imports, functions and classes listed in the overview

st.set_page_config(page_title=APP_NAME, page_icon="🧠", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Session state (the app's "memory" between reruns) ----------
DEFAULTS = {
    "code_input": "",          # text currently in the editor
    "uploaded_name": None,     # name of the uploaded file, if any
    "original_content": None,  # exact text of the uploaded file
    "last_file_id": None,      # lets us detect a NEW upload
    "upload_error": None,      # message if the upload failed
    "uploader_key": 0,         # changing this resets the file uploader widget
    "review_result": None,     # full result of the last review (includes its code)
}
for key, value in DEFAULTS.items():
    st.session_state.setdefault(key, value)


def normalize_newlines(text: str) -> str:
    """Make Windows (\\r\\n) and Mac (\\r) line endings the same as \\n."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def clear_all():
    """Reset the editor, upload status, and previous results."""
    st.session_state.code_input = ""
    st.session_state.uploaded_name = None
    st.session_state.original_content = None
    st.session_state.last_file_id = None
    st.session_state.upload_error = None
    st.session_state.review_result = None
    st.session_state.uploader_key += 1  # forces a fresh, empty uploader


def show_code_line(code_lines, line):
    if line and 1 <= line <= len(code_lines):
        st.code(code_lines[line - 1], language="python")


def render_syntax(result, code_lines):
    if not result.syntax_findings:
        st.success("No syntax errors found. Python can read this code.")
        if result.error_count:
            st.info(
                "Syntax only checks the grammar. The Code quality tab found "
                f"{result.error_count} likely error(s), for example names that are not defined."
            )
        return
    for f in result.syntax_findings:
        where = f"line {f.line}" if f.line else "unknown line"
        st.error(f"**{f.rule}** at {where}: {f.message}")
        show_code_line(code_lines, f.line)
        st.markdown(f"**What it means:** {f.explanation}")
        st.markdown(f"**How to fix it:** {f.suggestion}")


def render_ruff(result, code_lines):
    if result.ruff_skipped:
        st.info(
            "Ruff was skipped because the code has a syntax error. "
            "Fix the syntax error first, then click Review code again."
        )
        return
    if result.ruff_error:
        st.error(f"Ruff could not run: {result.ruff_error}")
        return
    if not result.ruff_findings:
        st.success("Ruff found no issues.")
        return

    st.write(
        f"Found **{len(result.ruff_findings)}** item(s): "
        f"{result.error_count} likely error(s), {result.warning_count} warning(s), "
        f"{result.style_count} style recommendation(s)."
    )
    icons = {"error": "🔴", "warning": "🟡", "info": "🔵"}
    labels = {"error": "Likely error", "warning": "Warning", "info": "Style recommendation"}
    severity_order = {"error": 0, "warning": 1, "info": 2}

    # Group repeated findings by rule so ten long-line warnings are one entry.
    groups = {}
    for f in result.ruff_findings:
        groups.setdefault(f.rule, []).append(f)
    ordered = sorted(
        groups.items(),
        key=lambda item: (severity_order.get(item[1][0].severity, 3), item[1][0].line or 0),
    )

    for rule, items in ordered:
        first = items[0]
        icon = icons.get(first.severity, "🔵")
        if len(items) == 1:
            title = f"{icon} {rule} · line {first.line} · {first.message}"
        else:
            title = f"{icon} {rule} · {len(items)} occurrences · first at line {first.line}"
        with st.expander(title):
            st.caption(labels.get(first.severity, "Finding"))
            st.markdown(f"**What it means:** {first.explanation}")
            st.markdown(f"**How to fix it:** {first.suggestion}")
            st.markdown("**Where:**")
            for f in items[:MAX_OCCURRENCES_SHOWN]:
                st.markdown(f"Line {f.line}: {f.message}")
                show_code_line(code_lines, f.line)
            hidden = items[MAX_OCCURRENCES_SHOWN:]
            if hidden:
                more = ", ".join(str(f.line) for f in hidden)
                st.caption(f"{len(hidden)} more at lines: {more}")


def render_complexity(result):
    if result.complexity_skipped:
        st.info("Complexity analysis was skipped because of the syntax error.")
        return
    if result.complexity_error:
        st.error(f"Radon could not run: {result.complexity_error}")
        return
    if not result.complexity:
        st.info("No functions or methods were found, so there is nothing to score.")
        return

    flagged = [r for r in result.complexity if r.flagged]
    if flagged:
        st.warning(
            f"{len(flagged)} of {len(result.complexity)} function(s) may be hard "
            "to maintain (score 6 or higher)."
        )
    else:
        st.success(f"All {len(result.complexity)} function(s) have low complexity (score 1-5).")

    table_lines = [
        "| Function | Line | Score | Rank | Worth a look? |",
        "|---|---:|---:|---|---|",
    ]
    for r in result.complexity:
        worth = "Yes" if r.flagged else "No"
        table_lines.append(f"| `{r.name}` | {r.line} | {r.complexity} | {r.rank} | {worth} |")
    st.markdown("\n".join(table_lines))

    for r in flagged:
        with st.expander(f"🟡 {r.name} · line {r.line} · score {r.complexity}"):
            st.markdown(f"**What it means:** {r.explanation}")
            st.markdown(f"**How to simplify:** {r.suggestion}")
    st.caption(
        "Ranks follow Radon's convention (A: 1-5, B: 6-10, C: 11-20, "
        "D: 21-30, E: 31-40, F: 41+). A high score is a hint to take a "
        "second look, not proof that the code is bad."
    )


def render_overview(result):
    if result.syntax_findings:
        st.info(
            "The overview was skipped because the code has a syntax error. "
            "Fix it first, then click Review code again."
        )
        return
    if result.overview_error:
        st.error(f"The overview could not be built: {result.overview_error}")
        return
    o = result.overview
    if o is None:
        st.info("No overview is available for this review.")
        return

    st.write(
        f"This file has **{o.code_line_count}** lines of code, with "
        f"**{len(o.functions)}** function(s), **{len(o.classes)}** class(es) "
        f"and **{len(o.imports)}** import(s)."
    )
    if o.module_doc:
        st.caption(f"The file describes itself as: {escape_markdown(o.module_doc)}")
    for note in o.notes:
        st.info(note)

    if o.imports:
        st.markdown("**Imports** (code this file borrows)")
        lines = []
        for imp in o.imports[:MAX_OVERVIEW_ITEMS]:
            purpose = f" for {imp.purpose}" if imp.purpose else ""
            lines.append(f"- `{imp.text}`: {imp.kind}{purpose}")
        st.markdown("\n".join(lines))

    if o.functions:
        st.markdown("**Functions** (named blocks of code you can reuse)")
        lines = []
        for f in o.functions[:MAX_OVERVIEW_ITEMS]:
            prefix = "async " if f.is_async else ""
            decorated = "".join(f", decorated with `@{d}`" for d in f.decorators)
            line = f"- `{prefix}{f.signature}` (line {f.line}{decorated}): {escape_markdown(f.summary())}"
            if f.doc:
                line += f" Its docstring says: {escape_markdown(f.doc)}"
            lines.append(line)
        st.markdown("\n".join(lines))
        if len(o.functions) > MAX_OVERVIEW_ITEMS:
            st.caption(f"Showing the first {MAX_OVERVIEW_ITEMS} of {len(o.functions)} functions.")

    if o.classes:
        st.markdown("**Classes** (blueprints for objects)")
        lines = []
        for c in o.classes[:MAX_OVERVIEW_ITEMS]:
            bases = f", based on {', '.join(f'`{b}`' for b in c.bases)}" if c.bases else ""
            methods = ", ".join(f"`{m}`" for m in c.methods) if c.methods else "none"
            line = f"- `{c.name}` (line {c.line}{bases}): methods: {methods}."
            if c.doc:
                line += f" Its docstring says: {escape_markdown(c.doc)}"
            lines.append(line)
        st.markdown("\n".join(lines))

    if o.has_main_guard or o.top_level_calls:
        st.markdown("**When the file runs**")
        if o.has_main_guard:
            st.markdown(
                "The block starting with `if __name__ == \"__main__\":` runs only when you run "
                "this file directly, not when another file imports it."
            )
        if o.top_level_calls:
            calls = ", ".join(f"`{c}`" for c in o.top_level_calls)
            st.markdown(f"It calls: {calls}.")

    st.caption(
        "This overview comes from reading the structure of your code. It does not run the "
        "code, and it cannot tell you whether the code works correctly."
    )


def render_findings_table(result, rows):
    if not rows:
        if (result.ruff_skipped or result.ruff_error
                or result.complexity_skipped or result.complexity_error):
            st.info(
                "There are no findings to list, but some checks were skipped or could not run. "
                "See the other tabs."
            )
        else:
            st.success("Nothing to list. These checks found nothing to report.")
        return

    col_sev, col_src = st.columns(2)
    chosen_severity = col_sev.multiselect(
        "Severity",
        options=list(SEVERITY_LABELS),
        default=list(SEVERITY_LABELS),
        format_func=SEVERITY_LABELS.get,
        key="severity_filter",
    )
    chosen_source = col_src.multiselect(
        "Source",
        options=list(SOURCE_LABELS),
        default=list(SOURCE_LABELS),
        format_func=SOURCE_LABELS.get,
        key="source_filter",
    )
    shown = filter_rows(rows, chosen_severity, chosen_source)
    st.caption(f"Showing {len(shown)} of {len(rows)} finding(s).")
    if shown:
        st.markdown(to_markdown_table(shown[:MAX_TABLE_ROWS]))
        if len(shown) > MAX_TABLE_ROWS:
            st.caption(f"The table shows the first {MAX_TABLE_ROWS}. The CSV has all {len(shown)}.")
    st.download_button(
        "Download shown findings (CSV)",
        data=to_csv(shown).encode("utf-8-sig"),
        file_name="findings.csv",
        mime="text/csv",
        disabled=not shown,
    )


def render_results(result, code):
    code_lines = code.splitlines()
    syntax_findings = result.syntax_findings

    # ---------- Summary dashboard ----------
    ran_ruff = not result.ruff_skipped and result.ruff_error is None
    ran_radon = not result.complexity_skipped and result.complexity_error is None

    if syntax_findings:
        st.error("Overall: the code has a syntax error, so the other checks were skipped.")
    elif not (ran_ruff and ran_radon):
        st.warning("Overall: some checks could not run, so this summary is incomplete.")
    elif (
        result.error_count + result.warning_count
        + result.style_count + result.flagged_function_count == 0
    ):
        st.success(
            "Overall: these checks found nothing to report. "
            "That does not guarantee the code is free of bugs."
        )
    else:
        st.info("Overall: there are items to look at. Details are in the tabs below.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Likely errors", result.error_count if (syntax_findings or ran_ruff) else "—")
    c2.metric("Warnings", result.warning_count if ran_ruff else "—")
    c3.metric("Style items", result.style_count if ran_ruff else "—")
    c4.metric("Complex functions", result.flagged_function_count if ran_radon else "—")
    c5.metric("Review time", f"{result.seconds:.2f} s")

    # ---------- Detail tabs ----------
    rows = collect_rows(result)
    tab_what, tab_all, tab_syntax, tab_ruff, tab_radon = st.tabs(
        [
            "What this code does",
            f"All findings ({len(rows)})",
            "Syntax",
            "Code quality (Ruff)",
            "Complexity (Radon)",
        ]
    )
    with tab_what:
        render_overview(result)
    with tab_all:
        render_findings_table(result, rows)
    with tab_syntax:
        render_syntax(result, code_lines)
    with tab_ruff:
        render_ruff(result, code_lines)
    with tab_radon:
        render_complexity(result)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

# Both pages are tabs so every widget is drawn on every run and keeps its state.
tab_review, tab_about = st.tabs(["Code Reviewer", "About the Project"])

with tab_review:
    st.markdown(HERO_HTML, unsafe_allow_html=True)

    left, right = st.columns([3, 2], gap="large")

    with left:
        st.markdown(
            section_html("01", "Code workspace", "Paste your code or upload a Python source file."),
            unsafe_allow_html=True,
        )
        # Containers fix the order on screen. The uploader must still be handled
        # BEFORE the text area is created, so an upload can fill the editor.
        editor_slot = st.container()
        upload_slot = st.container()
        status_slot = st.container()
        buttons_slot = st.container()

    with right:
        st.markdown(
            section_html("02", "Analysis modules", "What this app checks for you."),
            unsafe_allow_html=True,
        )
        st.markdown(MODULE_CARDS_HTML, unsafe_allow_html=True)

    # ---------- File upload ----------
    with upload_slot:
        uploaded = st.file_uploader(
            "Upload a .py file (optional, max 200 KB)",
            type=["py"],
            key=f"uploader_{st.session_state.uploader_key}",
        )

    # Only process the file when it is new, so edits in the editor are not overwritten.
    if uploaded is not None and uploaded.file_id != st.session_state.last_file_id:
        st.session_state.last_file_id = uploaded.file_id
        st.session_state.upload_error = None
        st.session_state.review_result = None  # new file -> old results are invalid

        safe_name = uploaded.name.replace("`", "")
        if uploaded.size > MAX_FILE_SIZE:
            st.session_state.upload_error = (
                f"`{safe_name}` is too large (limit is {MAX_FILE_SIZE // 1024} KB)."
            )
        else:
            try:
                text = uploaded.getvalue().decode("utf-8-sig")  # handles BOM too
            except UnicodeDecodeError:
                st.session_state.upload_error = (
                    f"`{safe_name}` is not valid UTF-8 text, so it cannot be read."
                )
            else:
                text = normalize_newlines(text)
                st.session_state.code_input = text
                st.session_state.original_content = text
                st.session_state.uploaded_name = safe_name  # name is display-only

    # ---------- Code editor ----------
    with editor_slot:
        code = st.text_area(
            "Python code",
            key="code_input",
            height=320,
            placeholder='def greet(name):\n    print(f"Hello, {name}!")\n\n\ngreet("World")',
        )

    # ---------- Upload errors and file status ----------
    with status_slot:
        if st.session_state.upload_error:
            st.error(st.session_state.upload_error)
        if st.session_state.uploaded_name:
            if normalize_newlines(code) == st.session_state.original_content:
                st.info(f"📄 **{st.session_state.uploaded_name}** — matches the uploaded file.")
            else:
                st.warning(
                    f"✏️ **{st.session_state.uploaded_name}** — modified "
                    "(the code above differs from the uploaded file)."
                )

    # ---------- Buttons ----------
    with buttons_slot:
        col_review, col_clear = st.columns(2, gap="small")
        review_clicked = col_review.button("Review code", type="primary", width="stretch")
        col_clear.button("Clear", on_click=clear_all, width="stretch")
        st.caption("Static analysis only. Your code is never executed.")

        if review_clicked:
            if not code.strip():
                st.warning("Please enter or upload some Python code first.")
                st.session_state.review_result = None
            else:
                with st.spinner("Reviewing your code..."):
                    st.session_state.review_result = review_code(code)

    # ---------- Results ----------
    st.markdown(
        section_html("03", "Analysis results", "Your latest review appears here."),
        unsafe_allow_html=True,
    )
    result = st.session_state.review_result
    if result is None:
        st.markdown(EMPTY_STATE_HTML, unsafe_allow_html=True)
    elif result.code != code:
        st.warning("The code has changed since the last review. Click **Review code** again.")
    else:
        render_results(result, code)

    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


with tab_about:
    st.markdown(
        section_html(
            "00",
            "Code review that helps you learn",
            "A learning assistant for beginner Python developers.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        """
Most code-review tools tell you *what* is wrong. This project also explains *why it matters*
and *what to try next*, in plain language.

**Available now**

- Paste Python code or upload a single `.py` file (up to 200 KB).
- Syntax check with line numbers and plain-language explanations. Submitted code is never run.
- Code quality review with Ruff (rule groups E, F and W), with likely errors kept apart from style advice.
- Complexity scores for each function with Radon, flagged at a score of 6 or higher.
- A plain-language overview of what the code is made of: imports, functions, classes and what runs.
- A findings table with severity and source filters and a CSV download.
- A summary of the results, tied to the exact code that was reviewed.

**Planned, not yet implemented**

- Evaluation on a set of labelled code examples.
- Optional LLM-written explanations. The core app does not need them.

**Limits to keep in mind**

- Static analysis cannot find every bug or security problem.
- Ruff and Radon run only when the syntax is valid, because Python reports one syntax error at a time.
- Complexity scores are a hint to take a second look, not a verdict on the code.
- Python only, one file at a time.
"""
    )
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)