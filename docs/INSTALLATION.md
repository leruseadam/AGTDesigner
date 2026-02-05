# AGT Label Maker - Installation Guide

## Quick Start

### Local Installation (macOS/Linux)

**Option 1: Automated (Recommended)**
```bash
./install_requirements.sh
```

**Option 2: Cross-platform Python Script**
```bash
python3 install_requirements.py
```

### PythonAnywhere Installation

```bash
python3 install_requirements.py
```

This will automatically:
- Install all dependencies from `requirements.txt`
- Apply the `docxcompose` patch to fix the pkg_resources deprecation warning

## What Gets Installed

The automated installation:
1. ✅ Installs all Python packages from `requirements.txt`
2. ✅ Patches `docxcompose` to use `importlib.metadata` instead of deprecated `pkg_resources`
3. ✅ Verifies the installation

## Manual Installation (Not Recommended)

If you prefer to install manually:

```bash
# Install dependencies
pip3 install --user -r requirements.txt

# Apply docxcompose patch
python3 patch_docxcompose.py
```

## Verification

To verify the installation worked correctly:

```bash
# Should produce NO warnings
python3 -Wall -c 'import docxcompose.properties'

# Test app imports
python3 -c 'import app; print("✓ Ready to run")'
```

## Running the Application

After installation:

```bash
python3 app.py
```

## Troubleshooting

**Issue**: `pkg_resources` deprecation warning appears
**Solution**: Run `python3 patch_docxcompose.py` to apply the fix

**Issue**: Installation fails on PythonAnywhere
**Solution**: Make sure you're using `--user` flag with pip:
```bash
pip3 install --user -r requirements.txt
```

## Why the Patch?

The `docxcompose` library uses the deprecated `pkg_resources` API, which will be removed in late November 2025. Our automated installation applies a patch that replaces it with the modern `importlib.metadata` API, ensuring your app continues working long-term.

For more details, see [DOCXCOMPOSE_FIX.md](DOCXCOMPOSE_FIX.md).

