"""Module 0 architecture guard: the portable brain must stay pure.

mini_agent may not import CLI, Textual/Rich, or any coding-app concern. This
test fails the moment someone sneaks a mini_coding-style dependency into the
core. It is the acceptance criterion from the learning guide, made executable.

Parsing is AST-based so it flags *actual imports*, not prose in docstrings.
"""

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_CORE_IMPORTS = {
    # coding-app / UI concerns the portable brain must not import
    "mini_coding",
    "textual",
    "rich",
    "typer",
    "click",
    "argparse",
    # local config paths are application concerns, not core ones
    "config",
}


def _import_roots(source: str) -> set[str]:
    """Return the root module names a file actually imports."""
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_mini_agent_does_not_import_coding_or_ui_layers() -> None:
    """Every mini_agent module imports only core-safe modules."""
    agent_dir = REPO_ROOT / "src" / "mini_agent"
    py_files = sorted(agent_dir.rglob("*.py"))
    assert py_files, "mini_agent source not found"
    for py in py_files:
        imported = _import_roots(py.read_text(encoding="utf-8"))
        violations = imported & FORBIDDEN_CORE_IMPORTS
        assert not violations, (
            f"{py.relative_to(REPO_ROOT)} imports forbidden core dependency(s) {sorted(violations)}"
        )
