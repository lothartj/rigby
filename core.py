"""Core functionality for whitespace package."""

import ast
from pathlib import Path
from typing import Union

def clean_source(source: str) -> str:
    """Clean source code by removing unnecessary empty lines within functions."""
    tree = ast.parse(source)
    lines = source.splitlines()
    to_remove = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            last_node = node.body[-1]
            end_line = last_node.end_lineno if hasattr(last_node, 'end_lineno') else last_node.lineno
            for i in range(start_line, end_line):
                if i >= len(lines):
                    continue
                if not lines[i].strip():
                    prev_non_empty = i > 0 and lines[i-1].strip()
                    next_non_empty = i < len(lines)-1 and lines[i+1].strip()
                    if prev_non_empty and next_non_empty:
                        to_remove.add(i)
    return "\n".join(line for i, line in enumerate(lines) if i not in to_remove)

def clean_file(file_path: Union[str, Path]) -> None:
    """Clean a Python file by removing unnecessary empty lines within functions."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    cleaned_source = clean_source(source)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_source)