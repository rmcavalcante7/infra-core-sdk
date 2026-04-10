from __future__ import annotations

import ast
from pathlib import Path


def test_source_tree_parses_with_python_312_grammar() -> None:
    source_root = Path(__file__).resolve().parents[1] / "src"
    syntax_errors: list[str] = []

    for path in source_root.rglob("*.py"):
        try:
            ast.parse(
                path.read_text(encoding="utf-8"),
                filename=str(path),
                feature_version=(3, 12),
            )
        except SyntaxError as exc:
            syntax_errors.append(f"{path}: {exc.msg} (line {exc.lineno})")

    assert not syntax_errors, "\n".join(syntax_errors)
