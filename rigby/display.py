"""Display components for rigby package."""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import List

DRAGON_ASCII = """
                 /\\    .-\" /
                /  ; .'  .'
               :   :/  .'
                \\  ;-.'
       .--\"\"\"\"--./_.'
     .'          './
    /  .----.      \\
   |  :      \\      |
   \\  :       \\    /
    \\  '-.__.-'   /
     '-.._____..'

   rigby CLEANER
"""

SIGN_OFF = (
    "[bright_white italic]authored by[/] [bold cyan]Lothar Tjipueja[/]  "
    "[dim]–[/] [link=https://github.com/lothartj]github.com/lothartj[/]"
)

console = Console()

def show_installation_complete():
    """Show a colorful installation complete message."""
    console.print()
    console.print(Panel(
        Text(DRAGON_ASCII, style="bold magenta"),
        title="[bold green]rigby Installed Successfully![/]",
        subtitle=SIGN_OFF,
        border_style="green",
    ))
    console.print()

def show_cleaning_complete(cleaned_files: List[str]):
    """Show a colorful completion message with cleaned files."""
    console.print()
    files_text = "\n".join([f"[green]✓[/] [cyan]{file}[/]" for file in cleaned_files])
    console.print(Panel(
        f"[bold green]Cleaning Complete![/]\n\n{files_text}",
        title="[bold blue]rigby Cleaner[/]",
        subtitle=SIGN_OFF,
        border_style="blue",
    ))
    console.print()