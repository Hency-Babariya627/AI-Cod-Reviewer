# Generated evaluation set: dataset card

405 files. Built by `generate_dataset.py` (seed 2026); regenerating gives identical files.

## How the labels were made
- 26 clean beginner programs (the *bases*) were written first; every base is verified to have no findings.
- Each flawed case applies one documented edit to a base (or three edits for the `multi` group). The expected rule and line come from the edit, not from any tool's output.
- Ruff, `compile()` and a complexity counter were run afterwards only to catch design mistakes. Disagreements found: 0.

## Balance
- Rules covered: 25. Expected findings per rule (min 13, max 14):
  E401 13, E402 13, E501 13, E701 13, E702 13, E703 13, E711 13, E712 13, E713 13, E714 13, E721 13, E722 13, E731 13, E741 13, F401 14, F541 13, F632 13, F811 13, F821 13, F841 13, W191 13, W291 13, W292 13, W293 13, W605 13
- Every base program is used in flawed cases between 10 and 11 times (of 26 bases).
- Where the edit sits (single and multi cases): {'main': 128, 'func': 190, 'method': 7}. Edits inside class methods are rare because only 2 of the 26 bases contain a class.
- Groups: single 250, multi 25, clean 52, near_miss 20, syntax 24, complexity 24, edge 10.
- Complexity group: 12 of 24 files contain a function with a score of 6 or more.
- Median file length (lines): clean 9.5, single 10.0, multi 15, syntax 10.5, complexity 14.5. Flawed and clean files have similar lengths, so file length does not give the answer away.

## Known limits
- Rule coverage is 25 of the many E, F and W rules; they were chosen as common beginner mistakes.
- Programs are short; real-world files are covered separately by `eval_data/real`.
- Findings inside class bodies are covered only for methods; nested functions, async code and decorators are not covered.
- Complexity labels follow Radon's documented counting rules and were counted by script, not by running Radon.
