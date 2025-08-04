# Virtual Environment Setup for LabelMaker

## ✅ Setup Complete!

Your virtual environment is now automatically activated when you enter the project directory. Here's what was configured:

## Automatic Activation

The virtual environment will automatically activate when you:
1. **Enter the project directory** - It activates automatically via your `.zshrc`
2. **Use the `labelmaker` command** - Quick activation from anywhere
3. **Run the provided scripts** - They handle activation internally

## Available Commands

### Quick Activation
```bash
labelmaker                    # Activate venv and navigate to project
activate_labelmaker          # Same as above
```

### Run Scripts (Auto-activate venv)
```bash
./run_app.sh                 # Run Flask app with auto venv activation
./activate_venv.sh           # Just activate the venv
```

### Manual Activation
```bash
source .venv/bin/activate    # Manual activation
```

## How It Works

1. **Auto-activation on directory entry**: When you `cd` into the project directory, the virtual environment automatically activates
2. **Preference order**: `.venv` is preferred over `venv`
3. **Fallback creation**: If no virtual environment exists, it will create one and install requirements

## Files Created/Modified

- `~/.zshrc` - Added auto-activation functions
- `activate_venv.sh` - Manual activation script
- `run_app.sh` - Updated to auto-activate venv
- `.envrc` - For direnv users (optional)
- `setup_auto_venv.sh` - Setup script (can be deleted)

## Troubleshooting

If you need to recreate the virtual environment:
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

You can now simply:
1. Navigate to your project: `cd /path/to/labelMaker`
2. The virtual environment activates automatically
3. Run your app: `python app.py` or `./run_app.sh`

No more manual activation needed! 🎉 