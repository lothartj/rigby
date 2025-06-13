"""rigby - A tool to remove empty lines and clean up rigby in Python files."""
import atexit
import os
from pathlib import Path
from .core import clean_file, clean_source
from .display import show_installation_complete
__version__ = "0.1.0"
__all__ = ["clean_file", "clean_source"]
INSTALL_MARKER = Path(__file__).parent / ".installed"
if not INSTALL_MARKER.exists():
    show_installation_complete()
    try:
        INSTALL_MARKER.touch()
    except Exception:
        pass