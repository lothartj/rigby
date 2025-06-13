"""Command line interface for rigby."""
import os
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
    """rigby - Clean up empty lines in Python files."""
    pass

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
def run(paths: List[str]):
    """Clean Python files by removing unnecessary empty lines within functions.
    Example usage:
        rigby run file.py    # Clean a single file
        rigby run .          # Clean all Python files in current directory
    """
    if not paths:
        console.print("[red]Please provide at least one file or directory path[/]", err=True)
        sys.exit(1)
    # Get the current working directory
    cwd = Path.cwd()
    cleaned_files = []
    for path in paths:
        # Convert to absolute path from current working directory
        abs_path = cwd / path
        if abs_path.is_file() and abs_path.suffix == '.py':
            console.print(f"[yellow]Cleaning[/] [cyan]{abs_path}[/]")
            try:
                clean_file(abs_path)
                cleaned_files.append(str(abs_path))
            except Exception as e:
                console.print(f"[red]Error processing {abs_path}: {e}[/]", err=True)
        elif abs_path.is_dir():
            for py_file in abs_path.rglob('*.py'):
                # Skip files in the rigby package directory
                if 'site-packages/rigby' in str(py_file):
                    continue
                console.print(f"[yellow]Cleaning[/] [cyan]{py_file}[/]")
                try:
                    clean_file(py_file)
                    cleaned_files.append(str(py_file))
                except Exception as e:
                    console.print(f"[red]Error processing {py_file}: {e}[/]", err=True)
        else:
            console.print(f"[yellow]Skipping {abs_path} - not a Python file or directory[/]", err=True)
    if cleaned_files:
        # Make paths relative for display
        relative_paths = [str(Path(f).relative_to(cwd)) for f in cleaned_files]
        show_cleaning_complete(relative_paths)
    else:
        console.print("[yellow]No Python files were cleaned.[/]")

def main():
    """Entry point for the CLI."""
    cli()