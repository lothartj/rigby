"""Command line interface for rigby."""

import sys
from pathlib import Path
from typing import List, Optional
import click
from rich.console import Console
from rich.panel import Panel
from .core import clean_file, clean_source
from .config import RigbyConfig
from .display import show_cleaning_complete

console = Console()

@click.group()
@click.version_option()
def cli():
    """Rigby - A Python code formatter focused on empty line management."""
    pass

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--config', type=click.Path(exists=True, dir_okay=False),
              help='Path to configuration file')
@click.option('--check', is_flag=True,
              help='Check if files would be reformatted without making changes')
@click.option('--diff', is_flag=True,
              help='Show diff of changes without applying them')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed output')
@click.option('--quiet', '-q', is_flag=True,
              help='Suppress all output except errors')
def run(paths: List[str], config: Optional[str], check: bool,
        diff: bool, verbose: bool, quiet: bool):
    """Clean Python files by managing empty lines."""
    if not paths:
        console.print("[yellow]No paths provided. Using current directory.[/]")
        paths = ["."]
    config_obj = RigbyConfig.from_file(Path(config) if config else None)
    modified_files = []
    error_files = []
    for path in paths:
        path = Path(path)
        if path.is_dir():
            python_files = path.rglob("*.py")
        else:
            python_files = [path]
        for file in python_files:
            try:
                if verbose and not quiet:
                    console.print(f"Processing {file}...")
                with open(file, 'r', encoding='utf-8') as f:
                    original = f.read()
                cleaned = clean_source(original, config_obj)
                if original != cleaned:
                    modified_files.append(str(file))
                    if diff and not quiet:
                        from difflib import unified_diff
                        diff_lines = unified_diff(
                            original.splitlines(keepends=True),
                            cleaned.splitlines(keepends=True),
                            fromfile=str(file),
                            tofile=str(file)
                        )
                        console.print(''.join(diff_lines))
                    if not check:
                        with open(file, 'w', encoding='utf-8') as f:
                            f.write(cleaned)
            except Exception as e:
                error_files.append((file, str(e)))
                if not quiet:
                    console.print(f"[red]Error processing {file}: {e}[/]")
    if not quiet:
        if modified_files:
            if check:
                console.print(f"\n[yellow]{len(modified_files)} files would be modified[/]")
                if verbose:
                    for file in modified_files:
                        console.print(f"  {file}")
            else:
                show_cleaning_complete(modified_files)
        if error_files:
            console.print(f"\n[red]{len(error_files)} files had errors[/]")
            if verbose:
                for file, error in error_files:
                    console.print(f"  {file}: {error}")
        if not modified_files and not error_files:
            console.print("\n[green]All files are correctly formatted![/]")
    if check and modified_files:
        sys.exit(1)

@cli.command()
def init():
    """Create a default configuration file."""
    config_file = Path(".rigby.toml")
    if config_file.exists():
        console.print("[red]Configuration file already exists![/]")
        sys.exit(1)
    config = RigbyConfig()
    import tomli_w
    with open(config_file, "wb") as f:
        tomli_w.dump({
            "lines_between_functions": config.lines_between_functions,
            "lines_between_classes": config.lines_between_classes,
            "preserve_docstring_spacing": config.preserve_docstring_spacing,
            "exclude_patterns": config.exclude_patterns,
            "sort_methods": config.sort_methods
        }, f)
    console.print(Panel.fit(
        "[green]Configuration file created![/]\n\n"
        "Edit .rigby.toml to customize formatting rules.\n"
        "You can also add settings to pyproject.toml under [tool.rigby].",
        title="Rigby Configuration"
    ))

def main():
    """Main entry point for the CLI."""
    cli()