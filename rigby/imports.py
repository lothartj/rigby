"""Import sorting and grouping functionality."""

import ast
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import List, Dict, Set

from .config import RigbyConfig, ImportGroup

@dataclass
class Import:
    """Represents a single import statement."""
    module: str
    names: List[str]
    is_from: bool
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int

def get_imports(tree: ast.AST) -> List[Import]:
    """Extract all imports from an AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(Import(
                    module=name.name,
                    names=[],
                    is_from=False,
                    lineno=node.lineno,
                    col_offset=node.col_offset,
                    end_lineno=node.end_lineno or node.lineno,
                    end_col_offset=node.end_col_offset or 0
                ))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(Import(
                module=module,
                names=[n.name for n in node.names],
                is_from=True,
                lineno=node.lineno,
                col_offset=node.col_offset,
                end_lineno=node.end_lineno or node.lineno,
                end_col_offset=node.end_col_offset or 0
            ))
    return imports

def group_imports(imports: List[Import], config: RigbyConfig) -> Dict[str, List[Import]]:
    """Group imports according to configuration."""
    groups: Dict[str, List[Import]] = {group.name: [] for group in config.import_groups}
    
    for imp in imports:
        module = imp.module
        assigned = False
        for group in config.import_groups:
            if any(fnmatch(module, pattern) for pattern in group.patterns):
                groups[group.name].append(imp)
                assigned = True
                break
        if not assigned:
            groups["standard_library"].append(imp)
    
    for group in groups.values():
        group.sort(key=lambda x: (x.module, x.names))
    
    return groups

def format_import(imp: Import) -> str:
    """Format an import statement."""
    if imp.is_from:
        names = ", ".join(sorted(imp.names))
        return f"from {imp.module} import {names}"
    return f"import {imp.module}"

def sort_and_format_imports(source: str, config: RigbyConfig) -> str:
    """Sort and format imports in the source code."""
    if not config.sort_imports:
        return source
    
    tree = ast.parse(source)
    imports = get_imports(tree)
    if not imports:
        return source
        
    import_lines = set()
    for imp in imports:
        for i in range(imp.lineno - 1, imp.end_lineno):
            import_lines.add(i)
    grouped_imports = group_imports(imports, config)
    new_imports = []
    for group_name, group_imports in grouped_imports.items():
        if group_imports:
            new_imports.extend(format_import(imp) for imp in group_imports)
            new_imports.append("")
    if new_imports and not new_imports[-1]:
        new_imports.pop()
    lines = source.splitlines()
    min_line = min(import_lines)
    max_line = max(import_lines)
    
    result = (
        lines[:min_line] +
        new_imports +
        lines[max_line + 1:]
    )
    
    return "\n".join(result) 