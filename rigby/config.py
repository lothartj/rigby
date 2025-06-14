"""Configuration handling for rigby."""

from pathlib import Path
from typing import List, Optional
import tomli
from pydantic import BaseModel, Field

class ImportGroup(BaseModel):
    """Configuration for import groups."""
    name: str = Field(description="Name of the import group")
    patterns: List[str] = Field(description="Patterns to match imports for this group")

class RigbyConfig(BaseModel):
    """Configuration settings for rigby."""
    lines_between_functions: int = Field(default=1, description="Number of empty lines between functions")
    lines_between_classes: int = Field(default=2, description="Number of empty lines between classes")
    preserve_docstring_spacing: bool = Field(default=True, description="Whether to preserve empty lines in docstrings")
    exclude_patterns: List[str] = Field(
        default=["venv/*", ".git/*", "__pycache__/*"],
        description="Glob patterns for files to exclude"
    )
    sort_methods: bool = Field(default=False, description="Whether to sort class methods alphabetically")
    
    # Import handling
    sort_imports: bool = Field(default=True, description="Whether to sort and group imports")
    import_groups: List[ImportGroup] = Field(
        default=[
            ImportGroup(name="future", patterns=["__future__"]),
            ImportGroup(name="standard_library", patterns=["typing", "pathlib", "os", "sys", "*"]),
            ImportGroup(name="third_party", patterns=["click.*", "rich.*", "pydantic.*", "loguru.*"]),
            ImportGroup(name="local", patterns=["rigby.*"]),
        ],
        description="Groups for organizing imports"
    )
    lines_between_import_groups: int = Field(default=1, description="Number of empty lines between import groups")

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "RigbyConfig":
        """Load configuration from a TOML file."""
        if config_path is None:
            locations = [
                Path("pyproject.toml"),
                Path(".rigby.toml"),
                Path.home() / ".config" / "rigby" / "config.toml"
            ]
            for loc in locations:
                if loc.exists():
                    config_path = loc
                    break
        if config_path and config_path.exists():
            with open(config_path, "rb") as f:
                try:
                    if config_path.name == "pyproject.toml":
                        data = tomli.load(f).get("tool", {}).get("rigby", {})
                    else:
                        data = tomli.load(f)
                    return cls(**data)
                except Exception as e:
                    from loguru import logger
                    logger.warning(f"Error loading config from {config_path}: {e}")
        return cls()