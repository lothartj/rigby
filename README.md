# rigby

<img src="https://raw.githubusercontent.com/lothartj/rigby/main/images/rigby.webp" alt="Rigby" width="200"/>

https://pypi.org/project/rigby/

A Python tool to clean up Python files by managing empty lines, with a focus on:
- Removing ALL empty lines within functions and classes.
- Maintaining exactly one empty line between functions.
- Maintaining exactly two empty lines between classes.

## Installation

Simply run:
```bash
pip install rigby
```

That's it! All dependencies will be automatically installed.

## Usage

You can use rigby either as a command-line tool or as a library in your Python code.

### Command Line Usage

```bash
rigby run file.py

rigby run file1.py file2.py

rigby run .
```

### Python Usage

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

## Features

- Removes ALL empty lines within functions and classes
- Maintains exactly one empty line between functions
- Maintains exactly two empty lines between classes
- Preserves code functionality while cleaning up spacing
- Supports both single file and directory processing
- Can be used as a CLI tool or Python library

## Dependencies

All of these will be installed automatically when you install the package:
- click>=8.0.0 - For command line interface
- loguru>=0.7.0 - For logging
- pydantic>=2.0.0 - For data validation
- typing-extensions>=4.0.0 - For type hints
- rich>=13.0.0 - For beautiful terminal output

## License

MIT License

rm -rf dist/ && python3 -m build
python3 -m twine upload dist/*
pip uninstall -y rigby && pip install --no-cache-dir rigby
