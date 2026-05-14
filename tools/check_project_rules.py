#!/usr/bin/env python3
"""Project-specific hygiene checks for Pyxel Rogue."""

from __future__ import annotations

import argparse
import ast
import importlib
import json
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    code: str
    message: str

    def format(self) -> str:
        return f"{self.code}: {self.message}"


def _load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data.pop("__summary__", None)
    return data


def _leaf_paths(data: object, prefix: tuple[str, ...] = ()) -> set[tuple[str, ...]]:
    if isinstance(data, dict):
        paths: set[tuple[str, ...]] = set()
        for key, value in data.items():
            if key == "__summary__":
                continue
            paths.update(_leaf_paths(value, prefix + (str(key),)))
        return paths
    return {prefix}


def check_nested_keys(label: str, en: dict, ja: dict) -> list[Issue]:
    issues: list[Issue] = []
    en_paths = _leaf_paths(en)
    ja_paths = _leaf_paths(ja)
    for path in sorted(en_paths - ja_paths):
        issues.append(Issue(label, f"missing ja key {'.'.join(path)}"))
    for path in sorted(ja_paths - en_paths):
        issues.append(Issue(label, f"extra ja key {'.'.join(path)}"))
    return issues


def check_root_modules(root: str) -> list[Issue]:
    issues: list[Issue] = []
    for name in sorted(os.listdir(root)):
        if name.startswith("rogue_") and name.endswith(".py"):
            issues.append(Issue("root-module", name))
    return issues


def _iter_python_files(root: str):
    skip_dirs = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        ".claude",
        ".worktrees",
        "__pycache__",
        "archive",
        "vendor",
    }
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for name in files:
            if name.endswith(".py"):
                yield os.path.join(base, name)


def check_text_rendering(root: str) -> list[Issue]:
    issues: list[Issue] = []
    for path in _iter_python_files(root):
        rel = os.path.relpath(path, root)
        if rel.startswith("tests" + os.sep):
            continue
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (
                isinstance(func, ast.Attribute)
                and func.attr == "text"
                and isinstance(func.value, ast.Name)
                and func.value.id == "pyxel"
            ):
                continue
            if rel == "rogue.py" and _enclosing_function(tree, node) == "txt":
                continue
            issues.append(Issue("text-render", f"{rel}:{node.lineno} use Game.txt/TextCatalog path"))
    return issues


def _call_uses_name(node: ast.AST, name: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id == name:
            return True
        if isinstance(child, ast.Attribute) and child.attr == name:
            return True
    return False


def _call_uses_name_prefix(node: ast.AST, prefix: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id.startswith(prefix):
            return True
        if isinstance(child, ast.Attribute) and child.attr.startswith(prefix):
            return True
    return False


def check_wrapper_comparison_tests(root: str) -> list[Issue]:
    issues: list[Issue] = []
    for path in _iter_python_files(root):
        rel = os.path.relpath(path, root)
        if not rel.startswith("tests" + os.sep):
            continue
        if rel == os.path.join("tests", "test_rogue_baseline.py"):
            continue
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=rel)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr in {"assertEqual", "assertIs"}):
                continue
            if len(node.args) < 2:
                continue
            left, right = node.args[:2]
            if _call_uses_name(left, "rogue") == _call_uses_name(right, "rogue"):
                continue
            other = right if _call_uses_name(left, "rogue") else left
            if _call_uses_name(other, "pyxel_rogue") or _call_uses_name_prefix(other, "rogue_"):
                issues.append(
                    Issue(
                        "wrapper-test",
                        f"{rel}:{node.lineno} compare extracted module to rogue.py wrapper via {func.attr}",
                    )
                )
    return issues


def _enclosing_function(tree: ast.AST, target: ast.AST) -> str | None:
    best: tuple[int, str] | None = None
    target_line = getattr(target, "lineno", 0)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.lineno <= target_line <= getattr(node, "end_lineno", node.lineno):
            span = getattr(node, "end_lineno", node.lineno) - node.lineno
            if best is None or span < best[0]:
                best = (span, node.name)
    return best[1] if best else None


def check_message_catalogs(root: str, strict_manifest: bool = False) -> list[Issue]:
    issues: list[Issue] = []
    msg_dir = os.path.join(root, "assets", "messages")
    en = _load_json(os.path.join(msg_dir, "en.json"))
    ja = _load_json(os.path.join(msg_dir, "ja.json"))
    manifest = _load_json(os.path.join(msg_dir, "manifest.json"))

    if strict_manifest:
        for key in sorted(set(en) - set(manifest)):
            issues.append(Issue("messages", f"missing manifest key {key}"))
    for key in sorted(set(manifest) - set(en)):
        issues.append(Issue("messages", f"extra manifest key {key}"))
    for key in sorted(set(ja) - set(en)):
        issues.append(Issue("messages", f"extra ja key {key}"))

    module = importlib.import_module("pyxel_rogue.rogue_message_catalogs")
    if getattr(module, "EN_MESSAGES") != en:
        issues.append(Issue("messages", "rogue_message_catalogs.EN_MESSAGES is out of sync"))
    if getattr(module, "JA_MESSAGES") != ja:
        issues.append(Issue("messages", "rogue_message_catalogs.JA_MESSAGES is out of sync"))
    return issues


def check_terms(root: str) -> list[Issue]:
    issues: list[Issue] = []
    terms_dir = os.path.join(root, "assets", "terms")
    en = _load_json(os.path.join(terms_dir, "en.json"))
    ja = _load_json(os.path.join(terms_dir, "ja.json"))
    issues.extend(check_nested_keys("terms", en, ja))

    module = importlib.import_module("pyxel_rogue.rogue_terms")
    if getattr(module, "EN_TERMS") != en:
        issues.append(Issue("terms", "rogue_terms.EN_TERMS is out of sync"))
    if getattr(module, "JA_TERMS") != ja:
        issues.append(Issue("terms", "rogue_terms.JA_TERMS is out of sync"))
    return issues


def find_unused_symbol_candidates(root: str) -> list[Issue]:
    root = os.path.abspath(root)
    definitions: dict[str, tuple[str, int, str]] = {}
    references: dict[str, int] = {}

    for path in _iter_python_files(root):
        rel = os.path.relpath(path, root)
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=rel)
        if not rel.startswith("tests" + os.sep):
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    definitions[node.name] = (rel, node.lineno, "function")
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                references[node.id] = references.get(node.id, 0) + 1
            elif isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load):
                references[node.attr] = references.get(node.attr, 0) + 1

    issues: list[Issue] = []
    for name, (rel, lineno, kind) in sorted(definitions.items()):
        if references.get(name, 0) == 0:
            issues.append(Issue("unused-candidate", f"{rel}:{lineno} {kind} {name}"))
    return issues


def check_project(root: str, strict_manifest: bool = True) -> list[Issue]:
    root = os.path.abspath(root)
    if root not in sys.path:
        sys.path.insert(0, root)
    issues: list[Issue] = []
    issues.extend(check_root_modules(root))
    issues.extend(check_text_rendering(root))
    issues.extend(check_wrapper_comparison_tests(root))
    issues.extend(check_message_catalogs(root, strict_manifest=strict_manifest))
    issues.extend(check_terms(root))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=os.getcwd())
    parser.add_argument("--strict-manifest", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-strict-manifest", action="store_true")
    parser.add_argument("--unused-report", action="store_true")
    args = parser.parse_args()
    issues = check_project(args.root, strict_manifest=not args.no_strict_manifest)
    unused_issues = find_unused_symbol_candidates(args.root) if args.unused_report else []
    for issue in issues:
        print(issue.format())
    for issue in unused_issues:
        print(issue.format())
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
