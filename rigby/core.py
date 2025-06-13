"""Core functionality for rigby package."""

import ast
from pathlib import Path
from typing import Union

def clean_source(source: str) -> str:
    """Clean source code by:
    1. Removing all empty lines within functions and classes
    2. Ensuring one empty line between functions
    3. Ensuring two empty lines between classes"""
    tree = ast.parse(source)
    lines = source.splitlines()
    to_remove = set()
    class_ends = set()
    function_ends = set()
    # First pass: identify empty lines within functions/classes and their boundaries
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1  # Convert to 0-based indexing
            last_node = node.body[-1]
            end_line = (last_node.end_lineno if hasattr(last_node, 'end_lineno') else last_node.lineno) - 1
            # Mark empty lines within the function/class for removal
            for i in range(start_line, end_line + 1):
                if i >= len(lines):
                    continue
                if not lines[i].strip():
                    to_remove.add(i)
            # Track where functions and classes end
            if isinstance(node, ast.ClassDef):
                class_ends.add(end_line)
            else:
                function_ends.add(end_line)
    # Create new source without removed lines
    cleaned_lines = []
    i = 0
    while i < len(lines):
        if i not in to_remove:
            cleaned_lines.append(lines[i])
            # Handle spacing between functions and classes
            if i in class_ends:
                cleaned_lines.extend([''] * 2)  # Two empty lines after classes
            elif i in function_ends:
                cleaned_lines.append('')  # One empty line after functions
        i += 1
    return '\n'.join(cleaned_lines)

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