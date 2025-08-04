# PythonAnywhere Installation Guide
# How to use the new requirements files

## Requirements Files Overview

1. **requirements_new.txt** - Recommended for most users
   - Tested, stable versions
   - Includes all necessary packages
   - Fixed version numbers for consistency

2. **requirements_minimal.txt** - For troubleshooting
   - Only essential packages
   - Use if you're having installation issues
   - Add more packages later once core works

3. **requirements_production.txt** - For production use
   - Version ranges for flexibility
   - Better for long-term maintenance
   - Allows minor updates within safe ranges

## Installation Steps

### Step 1: Choose Your Requirements File
```bash
# For most users (recommended):
pip install -r requirements_new.txt

# If having issues, try minimal first:
pip install -r requirements_minimal.txt

# For production deployment:
pip install -r requirements_production.txt
```

### Step 2: Pre-installation Setup
```bash
# Make sure you're in your virtual environment
source ~/.virtualenvs/myflaskapp-env/bin/activate

# Clear any cached packages
pip cache purge

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel
```

### Step 3: Install with Error Handling
```bash
# Install with specific flags to avoid build issues
pip install --no-cache-dir --only-binary=all -r requirements_new.txt

# If that fails, try without the binary-only flag
pip install --no-cache-dir -r requirements_new.txt
```

### Step 4: Verify Installation
```bash
python -c "import flask, pandas, numpy, PIL, docx, openpyxl; print('✅ All core packages imported successfully')"
```

### Step 5: Restart Your Web App
- Go to PythonAnywhere Web tab
- Click "Reload" button for your web app

## Troubleshooting

### If Pillow Still Fails:
```bash
# Install Pillow separately with specific version
pip install --no-cache-dir --only-binary=all Pillow==9.5.0
```

### If pandas/numpy Fail:
```bash
# Try older versions
pip install numpy==1.21.6 pandas==1.5.3
```

### If You Need docxcompose:
```bash
# Install it separately after everything else works
pip install docxcompose==1.4.0
```

## Package Version Explanations

- **Flask 2.3.3**: Stable LTS version, well-tested
- **Pillow 9.5.0**: Last version with reliable pre-built wheels
- **pandas 2.0.3**: Stable version with good NumPy compatibility
- **numpy 1.24.3**: Compatible with pandas 2.0.3
- **python-docx 0.8.11**: Stable version, widely used

## Next Steps After Installation

1. Test your app locally: `python app.py`
2. Check for import errors in PythonAnywhere logs
3. Restart your web app
4. Monitor error logs for any remaining issues
