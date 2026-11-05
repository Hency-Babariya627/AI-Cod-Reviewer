import time
from dataclasses import dataclass

from analyzers.radon_check import ComplexityResult, analyze_complexity
from analyzers.ruff_check import run_ruff
from analyzers.syntax_check import check_syntax
from models import Finding


@dataclass
class ReviewResult:
    """Everything one review produced, plus the exact code it was run on."""

    code: str
    syntax_findings: list[Finding]
    ruff_findings: list[Finding]
    ruff_error: str | None
    ruff_skipped: bool
    complexity: list[ComplexityResult]
    complexity_error: str | None
    complexity_skipped: bool
    seconds: float

    @property
    def error_count(self) -> int:
        return len(self.syntax_findings) + sum(
            f.severity == "error" for f in self.ruff_findings
        )

    @property
    def warning_count(self) -> int:
        return sum(f.severity == "warning" for f in self.ruff_findings)

    @property
    def style_count(self) -> int:
        return sum(f.severity == "info" for f in self.ruff_findings)

    @property
    def flagged_function_count(self) -> int:
        return sum(r.flagged for r in self.complexity)


def review_code(code: str) -> ReviewResult:
    """Run every analyzer once. Never executes the code."""
    start = time.perf_counter()

    syntax_findings = check_syntax(code)
    skip = bool(syntax_findings)  # Ruff and Radon only run on valid syntax

    ruff_findings, ruff_error = [], None
    complexity, complexity_error = [], None
    if not skip:
        ruff_findings, ruff_error = run_ruff(code)
        complexity, complexity_error = analyze_complexity(code)

    return ReviewResult(
        code=code,
        syntax_findings=syntax_findings,
        ruff_findings=ruff_findings,
        ruff_error=ruff_error,
        ruff_skipped=skip,
        complexity=complexity,
        complexity_error=complexity_error,
        complexity_skipped=skip,
        seconds=time.perf_counter() - start,
    )