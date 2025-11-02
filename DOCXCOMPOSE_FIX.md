# docxcompose pkg_resources Fix

## Issue
The `docxcompose` library uses the deprecated `pkg_resources` API, which will be removed in late November 2025.

## Solution Applied
1. **Installed from fork**: Using `git+https://github.com/tvuotila/docxcompose.git` in requirements.txt
2. **Applied local patch**: Ran `patch_docxcompose.py` to replace `pkg_resources` with `importlib.metadata`

## Automated Installation (Recommended)

Use the automated installation script that installs requirements AND applies the patch:

**On macOS/Linux:**
```bash
./install_requirements.sh
```

**On Windows or any platform:**
```bash
python3 install_requirements.py
```

**On PythonAnywhere:**
```bash
python3 install_requirements.py
```

## Manual Installation (if needed)
If you prefer to install manually:

```bash
pip install -r requirements.txt
python3 patch_docxcompose.py
```

Both methods will:
- Install docxcompose from the GitHub fork
- Patch the installed package to use `importlib.metadata` instead of `pkg_resources`

## Verification
Test that the warning is gone:

```bash
python3 -Wall -c 'import docxcompose.properties'
```

Should produce no output (no warnings).

## Future
Once `docxcompose` releases version 1.4.1 or higher on PyPI with the official fix, you can:
1. Revert `requirements.txt` to use `docxcompose>=1.4.1` (from PyPI)
2. Delete `patch_docxcompose.py` (no longer needed)
3. Reinstall with `pip install -r requirements.txt`

