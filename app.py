import streamlit as st
from pipeline import review_code

MAX_FILE_SIZE = 200 * 1024  # 200 KB limit for uploaded files

st.set_page_config(page_title="AI Code Reviewer", page_icon="🧠", layout="wide")


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


# ---------- Page header ----------
st.title("AI-Powered Code Reviewer")
st.caption("A learning assistant for beginner Python developers")

# ---------- File upload ----------
uploaded = st.file_uploader(
    "Upload a .py file (optional)",
    type=["py"],
    key=f"uploader_{st.session_state.uploader_key}",
)

# Only process the file when it is new, so edits in the editor are not overwritten.
if uploaded is not None and uploaded.file_id != st.session_state.last_file_id:
    st.session_state.last_file_id = uploaded.file_id
    st.session_state.upload_error = None
    st.session_state.review_result = None  # new file -> old results are invalid

    if uploaded.size > MAX_FILE_SIZE:
        st.session_state.upload_error = (
            f"'{uploaded.name}' is too large (limit is {MAX_FILE_SIZE // 1024} KB)."
        )
    else:
        try:
            text = uploaded.getvalue().decode("utf-8-sig")  # handles BOM too
        except UnicodeDecodeError:
            st.session_state.upload_error = (
                f"'{uploaded.name}' is not valid UTF-8 text, so it cannot be read."
            )
        else:
            text = normalize_newlines(text)
            st.session_state.code_input = text
            st.session_state.original_content = text
            st.session_state.uploaded_name = uploaded.name  # name is display-only

if st.session_state.upload_error:
    st.error(st.session_state.upload_error)

# ---------- Code editor ----------
code = st.text_area("Python code", key="code_input", height=300)

# ---------- File status ----------
if st.session_state.uploaded_name:
    if normalize_newlines(code) == st.session_state.original_content:
        st.info(f"📄 **{st.session_state.uploaded_name}** — matches the uploaded file.")
    else:
        st.warning(
            f"✏️ **{st.session_state.uploaded_name}** — modified "
            "(the code below differs from the uploaded file)."
        )

# ---------- Buttons ----------
col_review, col_clear, _ = st.columns([1, 1, 6])
review_clicked = col_review.button("Review Code", type="primary")
col_clear.button("Clear", on_click=clear_all)

if review_clicked:
    if not code.strip():
        st.warning("Please enter or upload some Python code first.")
        st.session_state.review_result = None
    else:
        with st.spinner("Reviewing your code..."):
            st.session_state.review_result = review_code(code)

# ---------- Results area ----------
result = st.session_state.review_result
if result is not None:
    if result.code != code:
        st.warning("The code has changed since the last review. Click **Review Code** again.")
    else:
        code_lines = code.splitlines()
        syntax_findings = result.syntax_findings

        st.subheader("Syntax check")
        if not syntax_findings:
            st.success("No syntax errors found. Python can read this code.")
        else:
            for f in syntax_findings:
                where = f"line {f.line}" if f.line else "unknown line"
                st.error(f"**{f.rule}** at {where}: {f.message}")
                if f.line and 1 <= f.line <= len(code_lines):
                    st.code(code_lines[f.line - 1], language="python")
                st.markdown(f"**What it means:** {f.explanation}")
                st.markdown(f"**How to fix it:** {f.suggestion}")

        st.subheader("Code quality (Ruff)")
        if result.ruff_skipped:
            st.info(
                "Ruff was skipped because the code has a syntax error. "
                "Fix the syntax error first, then click Review Code again."
            )
        elif result.ruff_error:
            st.error(f"Ruff could not run: {result.ruff_error}")
        elif not result.ruff_findings:
            st.success("Ruff found no issues.")
        else:
            st.write(
                f"Found **{len(result.ruff_findings)}** item(s): "
                f"{result.error_count} likely error(s), {result.warning_count} warning(s), "
                f"{result.style_count} style recommendation(s)."
            )
            icons = {"error": "🔴", "warning": "🟡", "info": "🔵"}
            labels = {"error": "Likely error", "warning": "Warning", "info": "Style"}
            for f in result.ruff_findings:
                title = f"{icons[f.severity]} {f.rule} · line {f.line} · {f.message}"
                with st.expander(title):
                    st.caption(labels[f.severity])
                    if f.line and 1 <= f.line <= len(code_lines):
                        st.code(code_lines[f.line - 1], language="python")
                    st.markdown(f"**What it means:** {f.explanation}")
                    st.markdown(f"**How to fix it:** {f.suggestion}")

        st.subheader("Complexity (Radon)")
        if result.complexity_skipped:
            st.info("Complexity analysis was skipped because of the syntax error above.")
        elif result.complexity_error:
            st.error(f"Radon could not run: {result.complexity_error}")
        elif not result.complexity:
            st.info("No functions or methods were found, so there is nothing to score.")
        else:
            flagged = [r for r in result.complexity if r.flagged]
            if flagged:
                st.warning(
                    f"{len(flagged)} of {len(result.complexity)} function(s) may be hard "
                    "to maintain (score 6 or higher)."
                )
            else:
                st.success(
                    f"All {len(result.complexity)} function(s) have low complexity (score 1-5)."
                )
            st.dataframe(
                [
                    {
                        "Function": r.name,
                        "Line": r.line,
                        "Score": r.complexity,
                        "Rank": r.rank,
                        "Worth a look?": "Yes" if r.flagged else "No",
                    }
                    for r in result.complexity
                ],
                width="stretch",
                hide_index=True,
            )
            for r in flagged:
                with st.expander(f"🟡 {r.name} · line {r.line} · score {r.complexity}"):
                    st.markdown(f"**What it means:** {r.explanation}")
                    st.markdown(f"**How to simplify:** {r.suggestion}")
            st.caption(
                "Ranks follow Radon's convention (A: 1-5, B: 6-10, C: 11-20, "
                "D: 21-30, E: 31-40, F: 41+). A high score is a hint to take a "
                "second look, not proof that the code is bad."
            )