# rigby

<div align="center">
<img src="https://raw.githubusercontent.com/lothartj/rigby/main/images/rigby.webp" alt="Rigby" width="200"/>

[![PyPI version](https://badge.fury.io/py/rigby.svg)](https://badge.fury.io/py/rigby)
[![Python Versions](https://img.shields.io/pypi/pyversions/rigby.svg)](https://pypi.org/project/rigby/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

## Overview

Rigby is a Python code formatter focused on managing empty lines to improve code readability. It follows a strict set of rules:

- ✨ Removes ALL empty lines within functions and classes
- 🔄 Maintains exactly one empty line between functions
- 🎯 Maintains exactly two empty lines between classes
- 🛡️ Preserves code functionality while cleaning

## Installation

```bash
pip install rigby
```

## Quick Start

### Command Line

```bash
rigby run file.py

rigby run file1.py file2.py

rigby run .
```

### Python API

```python
from rigby import clean_file, clean_source

clean_file("path/to/your/file.py")

source = '''
class MyClass:

    def foo():
        print("hello")

        print("world")

    def bar():
        print("bar")
'''
cleaned = clean_source(source)
```

## Before and After

```python
class MyClass:

    def method1(self):
        x = 1

        y = 2

        return x + y


    def method2(self):
        return True

class MyClass:
    def method1(self):
        x = 1
        y = 2
        return x + y

    def method2(self):
        return True
```

## Features

- 🧹 **Smart Cleanup**: Intelligently removes unnecessary empty lines while preserving code structure
- 🔍 **Selective Processing**: Format single files or entire directories
- 🛠️ **Dual Interface**: Use as a CLI tool or Python library
- ⚡ **Fast Processing**: Efficient parsing and formatting
- 🔒 **Safe Changes**: Preserves code functionality

## Configuration

No configuration needed! Rigby follows strict formatting rules to ensure consistency across all Python files.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| click | >=8.0.0 | Command line interface |
| loguru | >=0.7.0 | Logging functionality |
| pydantic | >=2.0.0 | Data validation |
| typing-extensions | >=4.0.0 | Type hints |
| rich | >=13.0.0 | Terminal output formatting |

## Development

```bash
git clone https://github.com/lothartj/rigby.git
cd rigby

pip install -e .

pytest

python -m build

python -m twine upload dist/*
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
