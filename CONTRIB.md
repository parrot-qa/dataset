# Authentication

Use the `create_secrets.py` utility to setup your environment:

```sh
python create_secrets.py --help
```

# Python Packages

A `venv` is preferred to keep packages clearly identified and organized.

```sh
python -m venv .venv

# Activate
source ./.venv/Scripts/activate  # For POSIX
./.venv/Scripts/Activate.ps1     # For Windows

pip install -r requirements.txt
```

If you add any new packages, please update requirements.txt as follows:

```
pip freeze > requirements.txt
```

# Coding guidelines

Recommended to use VS Code for easy configuration and setup (e.g. venv activated automatically).

Try to use standard Python naming conventions:

Token | Naming style
--- | ---
variables, functions, files | `lower_case_with_underscores` or `lowercase`
private variables | `_leading_underscore`
classes | `CapitalizedWords`

Code formatting on save is enabled by default for uniformity.
