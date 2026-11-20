"""Score the code reviewer against the labelled evaluation sets.

Run from the project root:   python evaluate.py

Reads labels from eval_data/cases/labels.json and eval_data/real/labels_real.json,
runs review_code() on every labelled file (the code is only analysed, never run),
and compares what the tool reported with the labels. Labels are never edited here.
"""

import json
import statistics
import time
from collections import Counter
from pathlib import Path

from pipeline import review_code

ROOT = Path(__file__).parent
SETS = {
    "own snippets": ROOT / "eval_data" / "cases" / "labels.json",
    "real files": ROOT / "eval_data" / "real" / "labels_real.json",
    "generated set": ROOT / "eval_data" / "generated" / "labels_generated.json",
}
RESULTS_FILE = ROOT / "eval_data" / "results.json"


def ratio(numerator: int, denominator: int) -> str:
    return "n/a" if denominator == 0 else f"{numerator / denominator:.2f}"


def short_name(name: str) -> str:
    """'Class.method' -> 'method' (labels use the bare function name)."""
    return name.split(".")[-1]


def score_set(set_name: str, labels_path: Path) -> dict:
    meta = json.loads(labels_path.read_text(encoding="utf-8"))
    base = labels_path.parent
    per_rule = {}  # rule -> Counter(tp, fp, fn)
    cx = Counter()  # complexity tp / fp / fn
    syn = Counter()  # syntax tp / fp / fn / tn
    clean_total = clean_with_findings = 0
    times = []
    problems = []  # human-readable differences to review
    tool_errors = []
    skipped_unlabelled = 0
    groups = {}  # group -> [files, files_with_a_difference]
    file_times = {}

    for case in meta["cases"]:
        if not case.get("labelled", True):
            skipped_unlabelled += 1
            continue
        file_name = case["file"]
        code = (base / file_name).read_bytes().decode("utf-8")
        # newline="" behaviour: keep line endings exactly as stored

        start = time.perf_counter()
        result = review_code(code)
        times.append(time.perf_counter() - start)
        file_times[file_name] = times[-1]
        problems_before = len(problems)

        # --- syntax ---
        detected = len(result.syntax_findings) > 0
        expected_syntax = case["syntax_error"]
        if expected_syntax and detected:
            syn["tp"] += 1
        elif expected_syntax and not detected:
            syn["fn"] += 1
            problems.append(f"{file_name}: syntax error NOT detected")
        elif detected:
            syn["fp"] += 1
            problems.append(f"{file_name}: syntax error reported but none expected")
        else:
            syn["tn"] += 1
        if expected_syntax:
            if not result.ruff_skipped or not result.complexity_skipped:
                problems.append(f"{file_name}: Ruff/Radon should be skipped on a syntax error")
            g = groups.setdefault(case.get("group", "-"), [0, 0])
            g[0] += 1
            g[1] += 1 if len(problems) > problems_before else 0
            continue  # nothing else is scored on files that cannot be parsed

        # --- Ruff (rule, line) ---
        if result.ruff_error:
            tool_errors.append(f"{file_name}: Ruff error: {result.ruff_error}")
        if result.complexity_error:
            tool_errors.append(f"{file_name}: Radon error: {result.complexity_error}")

        expected = Counter((e["rule"], e["line"]) for e in case["expected"])
        reported = Counter((f.rule, f.line) for f in result.ruff_findings)
        for key in set(expected) | set(reported):
            rule = key[0]
            bucket = per_rule.setdefault(rule, Counter())
            matched = min(expected[key], reported[key])
            bucket["tp"] += matched
            bucket["fn"] += expected[key] - matched
            bucket["fp"] += reported[key] - matched
            if expected[key] > matched:
                problems.append(f"{file_name}: MISSED {rule} on line {key[1]}")
            if reported[key] > matched:
                problems.append(f"{file_name}: UNEXPECTED {rule} on line {key[1]}")

        # --- complexity flags (by function name) ---
        expected_flags = Counter(case["flagged_functions"])
        reported_flags = Counter(short_name(r.name) for r in result.complexity if r.flagged)
        for name in set(expected_flags) | set(reported_flags):
            matched = min(expected_flags[name], reported_flags[name])
            cx["tp"] += matched
            cx["fn"] += expected_flags[name] - matched
            cx["fp"] += reported_flags[name] - matched
            if expected_flags[name] > matched:
                problems.append(f"{file_name}: function '{name}' expected to be flagged, was not")
            if reported_flags[name] > matched:
                problems.append(f"{file_name}: function '{name}' flagged but not expected")

        # --- clean files: any Ruff finding or flagged function is a false positive ---
        g = groups.setdefault(case.get("group", "-"), [0, 0])
        g[0] += 1
        g[1] += 1 if len(problems) > problems_before else 0
        if not case["expected"] and not case["flagged_functions"]:
            clean_total += 1
            if result.ruff_findings or any(r.flagged for r in result.complexity):
                clean_with_findings += 1

    tp = sum(b["tp"] for b in per_rule.values())
    fp = sum(b["fp"] for b in per_rule.values())
    fn = sum(b["fn"] for b in per_rule.values())

    print(f"\n=== {set_name} ({len(times)} files scored, {skipped_unlabelled} unlabelled skipped) ===")
    print(f"Ruff findings  : TP {tp}  FP {fp}  FN {fn}  "
          f"precision {ratio(tp, tp + fp)}  recall {ratio(tp, tp + fn)}")
    print(f"{'rule':8} {'TP':>3} {'FP':>3} {'FN':>3}  precision  recall")
    for rule in sorted(per_rule):
        b = per_rule[rule]
        print(f"{rule:8} {b['tp']:>3} {b['fp']:>3} {b['fn']:>3}  "
              f"{ratio(b['tp'], b['tp'] + b['fp']):>9}  {ratio(b['tp'], b['tp'] + b['fn']):>6}")
    print(f"Complexity flag: TP {cx['tp']}  FP {cx['fp']}  FN {cx['fn']}  "
          f"precision {ratio(cx['tp'], cx['tp'] + cx['fp'])}  "
          f"recall {ratio(cx['tp'], cx['tp'] + cx['fn'])}")
    print(f"Syntax errors  : detected {syn['tp']}, missed {syn['fn']}, "
          f"false alarms {syn['fp']}, correct on valid files {syn['tn']}")
    print(f"Clean files    : {clean_with_findings} of {clean_total} got a finding (false positives)")
    if times:
        print(f"Runtime/file   : median {statistics.median(times) * 1000:.0f} ms, "
              f"max {max(times) * 1000:.0f} ms, total {sum(times):.2f} s")
    if len(groups) > 1 or "-" not in groups:
        print("By group (files, files with a difference from the labels):")
        for name in sorted(groups):
            print(f"  {name:12} {groups[name][0]:>4} {groups[name][1]:>4}")
    sizes = {n: t for n, t in file_times.items() if n.startswith("edge_size_")}
    if sizes:
        print("Runtime by file size: " + ", ".join(f"{n[10:-3]} {t * 1000:.0f} ms" for n, t in sorted(sizes.items())))
    if tool_errors:
        print("TOOL ERRORS (not counted as 'no findings'):")
        for line in tool_errors:
            print("  -", line)
    print("Differences to review:" if problems else "No differences from the labels.")
    for line in problems:
        print("  -", line)

    return {
        "files_scored": len(times),
        "ruff": {"tp": tp, "fp": fp, "fn": fn},
        "per_rule": {rule: dict(b) for rule, b in per_rule.items()},
        "complexity": dict(cx),
        "syntax": dict(syn),
        "clean_files": {"total": clean_total, "with_findings": clean_with_findings},
        "runtime_seconds": {
            "median": statistics.median(times) if times else None,
            "max": max(times) if times else None,
            "total": sum(times),
        },
        "groups": {k: {"files": v[0], "with_difference": v[1]} for k, v in groups.items()},
        "file_seconds": file_times,
        "tool_errors": tool_errors,
        "differences": problems,
    }


def main() -> None:
    all_results = {}
    for set_name, path in SETS.items():
        if not path.exists():
            print(f"\n(skipping {set_name}: {path} not found)")
            continue
        all_results[set_name] = score_set(set_name, path)
    combined = {}
    for res in all_results.values():
        for rule, b in res["per_rule"].items():
            c = combined.setdefault(rule, Counter())
            for key in ("tp", "fp", "fn"):
                c[key] += b.get(key, 0)
    if len(all_results) > 1:
        tp = sum(b["tp"] for b in combined.values())
        fp = sum(b["fp"] for b in combined.values())
        fn = sum(b["fn"] for b in combined.values())
        print("\n=== ALL SETS COMBINED ===")
        print(f"Ruff findings  : TP {tp}  FP {fp}  FN {fn}  "
              f"precision {ratio(tp, tp + fp)}  recall {ratio(tp, tp + fn)}")
        print(f"{'rule':8} {'TP':>3} {'FP':>3} {'FN':>3}  precision  recall")
        for rule in sorted(combined):
            b = combined[rule]
            print(f"{rule:8} {b['tp']:>3} {b['fp']:>3} {b['fn']:>3}  "
                  f"{ratio(b['tp'], b['tp'] + b['fp']):>9}  {ratio(b['tp'], b['tp'] + b['fn']):>6}")
        cx_tp = sum(r["complexity"].get("tp", 0) for r in all_results.values())
        cx_fp = sum(r["complexity"].get("fp", 0) for r in all_results.values())
        cx_fn = sum(r["complexity"].get("fn", 0) for r in all_results.values())
        print(f"Complexity flag: TP {cx_tp}  FP {cx_fp}  FN {cx_fn}  "
              f"precision {ratio(cx_tp, cx_tp + cx_fp)}  recall {ratio(cx_tp, cx_tp + cx_fn)}")
        clean_t = sum(r["clean_files"]["total"] for r in all_results.values())
        clean_f = sum(r["clean_files"]["with_findings"] for r in all_results.values())
        print(f"Clean files    : {clean_f} of {clean_t} got a finding (false positives)")
    RESULTS_FILE.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nFull results saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
