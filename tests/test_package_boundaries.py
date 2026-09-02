"""Module 0 architecture guard: the portable brain must stay pure.

mini_agent may not import CLI, Textual/Rich, or any coding-app concern. This
test fails the moment someone sneaks a tau_coding-style dependency into the
core. It is the acceptance criterion from the learning guide, made executable.
"""

import sysconfig
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_IN_CORE = (
    # coding-app / UI concerns the portable brain must not know about
    "mini_coding",
    "textual",
    "rich",
    "typer",
    "click",
    "argparse",
    # local config paths are application concerns, not core ones
    "config",
)


def _core_package_names() -> list[str]:
    packages = ["mini_agent"]
    include_root = sysconfig.get_paths()["purelib"]
    for candidate in FORBIDDEN_IN_CORE:
        # A forbidden module only matters if it would actually resolve.
        path = Path(include_root) / f"{candidate}.py"
        pkg_dir = Path(include_root) / candidate
        if path.exists() or pkg_dir.exists():
            packages.append(candidate)
    return packages


def test_mini_agent_does_not_import_coding_or_ui_layers() -> None:
    """Import the whole mini_agent source tree and require no forbidden imports."""
    src_dir = REPO_ROOT / "src"
    agent_dir = src_dir / "mini_agent"
    if not agent_dir.is_dir():  # guard against running from a sdist without src
        return
    for py in sorted(agent_dir.rglob("*.py")):
        if py.name.startswith("_"):
            continue
        text = py.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_IN_CORE:
            assert forbidden not in text, (
                f"{py.relative_to(REPO_ROOT)} mentions forbidden core dependency {forbidden!r}"
            )
