"""Core functionality for rigby package."""

from loguru import logger
import ast
from pathlib import Path
from typing import Union, List, Tuple

from .config import RigbyConfig
from .imports import sort_and_format_imports

def clean_source(source: str, config: RigbyConfig = None) -> str:
    """Clean source code by managing empty lines according to configuration."""
    if config is None:
        config = RigbyConfig()
    source = sort_and_format_imports(source, config)
        
    tree = ast.parse(source)
    lines = source.splitlines()
    to_remove = set()
    class_ends = set()
    function_ends = set()
    nodes: List[Tuple[int, ast.AST]] = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            last_node = node.body[-1]
            end_line = (last_node.end_lineno if hasattr(last_node, 'end_lineno') else last_node.lineno) - 1
            nodes.append((start_line, node))
            for i in range(start_line, end_line + 1):
                if i >= len(lines):
                    continue
                if not lines[i].strip():
                    if config.preserve_docstring_spacing and is_in_docstring(node, i):
                        continue
                    to_remove.add(i)
            if isinstance(node, ast.ClassDef):
                class_ends.add(end_line)
            else:
                function_ends.add(end_line)
    
    if config.sort_methods:
        nodes.sort(key=lambda x: (x[0], x[1].__class__.__name__, x[1].name))
    
    cleaned_lines = []
    i = 0
    while i < len(lines):
        if i not in to_remove:
            cleaned_lines.append(lines[i])
            if i in class_ends:
                cleaned_lines.extend([''] * config.lines_between_classes)
            elif i in function_ends:
                cleaned_lines.extend([''] * config.lines_between_functions)
        i += 1
    
    return '\n'.join(cleaned_lines)

def is_in_docstring(node: ast.AST, line_no: int) -> bool:
    """Check if a line number falls within a node's docstring."""
    if not ast.get_docstring(node):
        return False
    docstring_node = node.body[0] if isinstance(node.body[0], ast.Expr) else None
    if not docstring_node or not isinstance(docstring_node.value, ast.Str):
        return False
    return node.lineno <= line_no <= docstring_node.end_lineno

def clean_file(file_path: Union[str, Path], config: RigbyConfig = None) -> None:
    """Clean a Python file according to configuration."""
    if config is None:
        config = RigbyConfig()
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    from fnmatch import fnmatch
    if any(fnmatch(str(file_path), pattern) for pattern in config.exclude_patterns):
        logger.debug(f"Skipping excluded file: {file_path}")
        return
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    cleaned_source = clean_source(source, config)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_source)