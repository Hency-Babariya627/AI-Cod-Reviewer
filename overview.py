"""A plain-language overview of what a piece of Python code is made of.

Built with Python's ast module, which only READS the code as a tree. Nothing is
executed. The overview describes structure (imports, functions, classes, what a
function takes and does). It cannot tell whether the code is correct.

No Streamlit code here, so it can be tested on its own.
"""
import ast
import sys
import warnings
from dataclasses import dataclass, field

MAX_TEXT = 40  # longest piece of user text (default value, docstring line) we keep

KNOWN_STDLIB = {
    "os": "operating-system tasks such as files and folders",
    "sys": "Python and command-line details",
    "math": "maths functions",
    "random": "random numbers",
    "json": "reading and writing JSON data",
    "csv": "reading and writing CSV files",
    "re": "pattern matching in text (regular expressions)",
    "datetime": "dates and times",
    "time": "time and delays",
    "pathlib": "file and folder paths",
    "collections": "extra container types such as Counter and defaultdict",
    "itertools": "tools for looping",
    "subprocess": "running other programs",
    "logging": "recording log messages",
    "typing": "type hints",
    "dataclasses": "simple classes that mostly hold data",
    "argparse": "reading command-line options",
    "unittest": "writing tests",
    "sqlite3": "small SQL databases",
}
KNOWN_EXTERNAL = {
    "streamlit": "building web apps",
    "pandas": "tables of data",
    "numpy": "numerical arrays",
    "requests": "web requests",
    "matplotlib": "charts",
}


@dataclass
class ImportInfo:
    line: int
    text: str          # for example "import os" or "from math import sqrt"
    kind: str          # "standard library", "external package", or "same project"
    purpose: str = ""  # only for modules we know well


@dataclass
class FunctionInfo:
    name: str          # "greet" or "Calc.add"
    line: int
    params: list
    is_async: bool = False
    returns_value: bool = False
    is_generator: bool = False
    prints: bool = False
    reads_input: bool = False
    opens_files: bool = False
    loops: bool = False
    decisions: bool = False
    handles_errors: bool = False
    calls_own: list = field(default_factory=list)
    decorators: list = field(default_factory=list)
    doc: str = ""

    @property
    def signature(self):
        return f"{self.name}({', '.join(self.params)})"

    def summary(self):
        """One plain-English sentence about what this function does."""
        named = [p for p in self.params if not p.startswith("*")]
        optional = [p for p in named if "=" in p]
        extra = len(named) != len(self.params)  # *args or **kwargs present
        n = len(named)
        if n == 0 and not extra:
            first = "takes no inputs"
        else:
            first = f"takes {n} input{'s' if n != 1 else ''}"
            if optional:
                first += f" ({len(optional)} optional)"
            if extra:
                first += ", plus any number of extra inputs"
        parts = [first]
        if self.reads_input:
            parts.append("asks the user to type something")
        if self.opens_files:
            parts.append("opens a file")
        if self.decisions:
            parts.append("makes decisions with if")
        if self.loops:
            parts.append("repeats steps in a loop")
        if self.handles_errors:
            parts.append("handles errors with try/except")
        if self.calls_own:
            parts.append("uses " + ", ".join(self.calls_own))
        if self.prints:
            parts.append("prints text")
        if self.is_generator:
            parts.append("produces values one at a time (a generator)")
        elif self.returns_value:
            parts.append("returns a value")
        else:
            parts.append("does not return a value")
        return "; ".join(parts) + "."


@dataclass
class ClassInfo:
    name: str
    line: int
    bases: list
    methods: list
    doc: str = ""


@dataclass
class Overview:
    line_count: int
    code_line_count: int
    imports: list
    functions: list
    classes: list
    top_level_calls: list
    has_main_guard: bool
    notes: list
    module_doc: str = ""


# ---------- small helpers ----------

def clean_text(text, limit=MAX_TEXT):
    """One line, no backticks, shortened. Safe to put inside a Markdown code span."""
    text = " ".join(str(text).split()).replace("`", "'")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def escape_markdown(text):
    """Escape characters that Markdown could turn into links, colours or maths."""
    out = []
    for ch in str(text):
        out.append("\\" + ch if ch in "\\`*_[]<>#|~$:!()" else ch)
    return "".join(out)


def _first_doc_line(node):
    doc = ast.get_docstring(node)
    return clean_text(doc.strip().splitlines()[0]) if doc and doc.strip() else ""


def _walk_local(node):
    """Walk a function or class body but do not enter nested functions or classes."""
    stack = list(ast.iter_child_nodes(node))
    while stack:
        n = stack.pop()
        yield n
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            stack.extend(ast.iter_child_nodes(n))


def _call_name(call):
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return clean_text(ast.unparse(func))
    return ""


def _param_strings(args, skip_first):
    positional = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    out = []
    for arg, default in zip(positional, defaults):
        out.append(arg.arg if default is None else f"{arg.arg}={clean_text(ast.unparse(default), 20)}")
    if skip_first and out and positional[0].arg in ("self", "cls"):
        out = out[1:]
    if args.vararg:
        out.append("*" + args.vararg.arg)
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        out.append(arg.arg if default is None else f"{arg.arg}={clean_text(ast.unparse(default), 20)}")
    if args.kwarg:
        out.append("**" + args.kwarg.arg)
    return out


def _describe_function(node, own_names, class_name=None):
    info = FunctionInfo(
        name=f"{class_name}.{node.name}" if class_name else node.name,
        line=node.lineno,
        params=_param_strings(node.args, skip_first=class_name is not None),
        is_async=isinstance(node, ast.AsyncFunctionDef),
        decorators=[clean_text(ast.unparse(d), 30) for d in node.decorator_list],
        doc=_first_doc_line(node),
    )
    called_own = []  # (line, column, name), sorted into source order below
    for n in _walk_local(node):
        if isinstance(n, ast.Return) and n.value is not None and not (
            isinstance(n.value, ast.Constant) and n.value.value is None
        ):
            info.returns_value = True
        elif isinstance(n, (ast.Yield, ast.YieldFrom)):
            info.is_generator = True
        elif isinstance(n, (ast.For, ast.AsyncFor, ast.While)):
            info.loops = True
        elif isinstance(n, ast.If):
            info.decisions = True
        elif isinstance(n, ast.Try):
            info.handles_errors = True
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            name = n.func.id
            if name == "print":
                info.prints = True
            elif name == "input":
                info.reads_input = True
            elif name == "open":
                info.opens_files = True
            elif name in own_names and name != node.name:
                called_own.append((n.lineno, n.col_offset, name))
    ordered = []
    for _, _, name in sorted(called_own):
        if name not in ordered:
            ordered.append(name)
    info.calls_own = ordered[:5]
    return info


def _import_infos(tree):
    stdlib = getattr(sys, "stdlib_module_names", frozenset())
    infos, seen = [], set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                text = f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                root = alias.name.split(".")[0]
                infos.append((node.lineno, text, root, False))
        elif isinstance(node, ast.ImportFrom):
            names = ", ".join(a.name for a in node.names)
            module = "." * node.level + (node.module or "")
            text = clean_text(f"from {module} import {names}", 60)
            root = (node.module or "").split(".")[0]
            infos.append((node.lineno, text, root, node.level > 0))
    result = []
    for line, text, root, relative in sorted(infos):
        if text in seen:
            continue
        seen.add(text)
        if relative:
            kind, purpose = "same project", ""
        elif root in stdlib:
            kind, purpose = "standard library", KNOWN_STDLIB.get(root, "")
        else:
            kind, purpose = "external package or your own module", KNOWN_EXTERNAL.get(root, "")
        result.append(ImportInfo(line=line, text=clean_text(text, 60), kind=kind, purpose=purpose))
    return result


def _is_main_guard(node):
    return (
        isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and len(node.test.comparators) == 1
        and isinstance(node.test.comparators[0], ast.Constant)
        and node.test.comparators[0].value == "__main__"
    )


def _top_level_calls(statements):
    calls = []
    for stmt in statements:
        value = None
        if isinstance(stmt, ast.Expr):
            value = stmt.value
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            value = stmt.value
        if isinstance(value, ast.Call):
            name = _call_name(value)
            if name and name not in calls:
                calls.append(name)
    return calls


# ---------- main entry point ----------

def describe_code(code):
    """Return (Overview, None), or (None, error_message) if the code cannot be read.

    Never runs the code. Call it only on code that already passed the syntax check.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(code, filename="<submitted>")
    except SyntaxError as err:
        return None, f"The code could not be read: {err.msg}"
    except (ValueError, RecursionError, MemoryError) as err:
        return None, f"The code could not be read: {str(err) or type(err).__name__}"

    try:
        own_names = {
            n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        functions, classes = [], []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(_describe_function(node, own_names))
            elif isinstance(node, ast.ClassDef):
                methods = [
                    n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                classes.append(ClassInfo(
                    name=node.name,
                    line=node.lineno,
                    bases=[clean_text(ast.unparse(b), 30) for b in node.bases],
                    methods=[m.name for m in methods],
                    doc=_first_doc_line(node),
                ))
                functions.extend(_describe_function(m, own_names, node.name) for m in methods)

        top_calls = _top_level_calls(tree.body)
        has_guard = False
        for node in tree.body:
            if _is_main_guard(node):
                has_guard = True
                for call in _top_level_calls(node.body):
                    if call not in top_calls:
                        top_calls.append(call)

        notes = []
        all_calls = {n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        if "input" in all_calls:
            notes.append("It asks the user to type something with input().")
        if "open" in all_calls:
            notes.append("It opens files with open().")
        if all_calls & {"eval", "exec"}:
            notes.append(
                "It calls eval() or exec(), which run text as code. That is risky if the text "
                "comes from someone else."
            )

        lines = code.splitlines()
        code_lines = sum(1 for ln in lines if ln.strip() and not ln.strip().startswith("#"))
        return Overview(
            line_count=len(lines),
            code_line_count=code_lines,
            imports=_import_infos(tree),
            functions=functions,
            classes=classes,
            top_level_calls=top_calls[:10],
            has_main_guard=has_guard,
            notes=notes,
            module_doc=_first_doc_line(tree),
        ), None
    except (RecursionError, MemoryError) as err:
        return None, f"The code is too complex to summarise: {type(err).__name__}"