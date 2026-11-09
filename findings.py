"""Turn one ReviewResult into a single list of findings for a table and a CSV download.

No Streamlit code here, so it can be tested on its own. Radon is not a list of
problems, so only functions that Radon flagged (score 6 or higher) become rows,
with severity "info".
"""
import csv
import io

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}
SEVERITY_LABELS = {"error": "Likely error", "warning": "Warning", "info": "Style / info"}
SOURCE_LABELS = {"syntax": "Syntax", "ruff": "Ruff", "radon": "Radon"}

CSV_COLUMNS = ["Source", "Rule", "Severity", "Line", "Message", "What it means", "How to fix it"]
TABLE_COLUMNS = ["Source", "Rule", "Severity", "Line", "Message"]


def _row(source, rule, severity, line, message, explanation, suggestion):
    return {
        "source": source, "rule": rule, "severity": severity, "line": line,
        "message": message, "explanation": explanation, "suggestion": suggestion,
    }


def collect_rows(result):
    """All findings from one review, most serious first, then by line."""
    rows = []
    for f in list(result.syntax_findings) + list(result.ruff_findings):
        rows.append(_row(f.source, f.rule, f.severity, f.line, f.message, f.explanation, f.suggestion))
    for r in result.complexity:
        if r.flagged:
            message = f"'{r.name}' has a complexity score of {r.complexity} (rank {r.rank})"
            rows.append(_row("radon", f"CC-{r.rank}", "info", r.line, message, r.explanation, r.suggestion))
    rows.sort(key=lambda x: (SEVERITY_ORDER.get(x["severity"], 3), x["line"] or 0, x["rule"]))
    return rows


def filter_rows(rows, severities, sources=None):
    """Keep rows with a chosen severity and, if sources is given, a chosen source."""
    keep_severity = set(severities)
    keep_source = None if sources is None else set(sources)
    return [
        r for r in rows
        if r["severity"] in keep_severity and (keep_source is None or r["source"] in keep_source)
    ]


def _safe_cell(value):
    """Stop spreadsheet programs from treating text as a formula (CSV injection)."""
    text = "" if value is None else str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def to_csv(rows):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for r in rows:
        writer.writerow([
            _safe_cell(SOURCE_LABELS.get(r["source"], r["source"])),
            _safe_cell(r["rule"]),
            _safe_cell(SEVERITY_LABELS.get(r["severity"], r["severity"])),
            "" if r["line"] is None else r["line"],
            _safe_cell(r["message"]),
            _safe_cell(r["explanation"]),
            _safe_cell(r["suggestion"]),
        ])
    return out.getvalue()


def _md_cell(value):
    text = "" if value is None else str(value)
    return " ".join(text.split()).replace("|", "\\|")


def to_markdown_table(rows):
    lines = ["| " + " | ".join(TABLE_COLUMNS) + " |", "|---|---|---|---:|---|"]
    for r in rows:
        lines.append(
            "| " + " | ".join([
                _md_cell(SOURCE_LABELS.get(r["source"], r["source"])),
                f"`{_md_cell(r['rule'])}`",
                _md_cell(SEVERITY_LABELS.get(r["severity"], r["severity"])),
                "" if r["line"] is None else str(r["line"]),
                _md_cell(r["message"]),
            ]) + " |"
        )
    return "\n".join(lines)