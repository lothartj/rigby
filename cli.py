"""Command line interface for whitespace."""
import sys
from pathlib import Path
from typing import List
import click
from rich.console import Console
from .core import clean_file
from .display import show_cleaning_complete

console = Console()

@click.group()
def cli():
    """Whitespace - Clean up empty lines in Python files."""
    pass

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def run(paths: List[str]):
    """Clean Python files by removing unnecessary empty lines within functions.
    Example usage:
        whitespace run file.py    # Clean a single file
        whitespace run .          # Clean all Python files in current directory
    """
    if not paths:
        console.print("[red]Please provide at least one file or directory path[/]", err=True)
        sys.exit(1)
    cleaned_files = []
    for path in paths:
        path = Path(path)
        if path.is_file() and path.suffix == '.py':
            console.print(f"[yellow]Cleaning[/] [cyan]{path}[/]")
            try:
                clean_file(path)
                cleaned_files.append(str(path))
            except Exception as e:
                console.print(f"[red]Error processing {path}: {e}[/]", err=True)
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                console.print(f"[yellow]Cleaning[/] [cyan]{py_file}[/]")
                try:
                    clean_file(py_file)
                    cleaned_files.append(str(py_file))
                except Exception as e:
                    console.print(f"[red]Error processing {py_file}: {e}[/]", err=True)
        else:
            console.print(f"[yellow]Skipping {path} - not a Python file or directory[/]", err=True)

    if cleaned_files:
        show_cleaning_complete(cleaned_files)
    else:
        console.print("[yellow]No Python files were cleaned.[/]")

def main():
    """Entry point for the CLI."""
    cli()