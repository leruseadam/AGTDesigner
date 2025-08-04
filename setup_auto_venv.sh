#!/bin/bash

# Setup script for automatic virtual environment activation
# This script will add the necessary configuration to your shell profile

echo "Setting up automatic virtual environment activation for labelMaker..."

# Get the current directory
PROJECT_DIR="$(pwd)"
PROJECT_NAME="labelMaker"

# Create a function that will be added to shell profile
FUNCTION_CODE="
# Auto-activate labelMaker virtual environment
function activate_labelmaker() {
    cd \"$PROJECT_DIR\"
    if [ -d \".venv\" ]; then
        source .venv/bin/activate
        echo \"✅ Virtual environment activated for $PROJECT_NAME\"
        echo \"🚀 You can now run: python app.py or ./run_app.sh\"
    elif [ -d \"venv\" ]; then
        source venv/bin/activate
        echo \"✅ Virtual environment activated for $PROJECT_NAME (venv)\"
        echo \"🚀 You can now run: python app.py or ./run_app.sh\"
    else
        echo \"❌ No virtual environment found. Creating one...\"
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        echo \"✅ Virtual environment created and activated!\"
    fi
}

# Alias for quick activation
alias labelmaker=\"activate_labelmaker\"
"

# Detect shell and add to appropriate profile
if [[ "$SHELL" == *"zsh"* ]]; then
    PROFILE_FILE="$HOME/.zshrc"
    echo "Detected zsh shell, adding to $PROFILE_FILE"
elif [[ "$SHELL" == *"bash"* ]]; then
    PROFILE_FILE="$HOME/.bashrc"
    echo "Detected bash shell, adding to $PROFILE_FILE"
else
    echo "Unknown shell: $SHELL"
    echo "Please manually add the following to your shell profile:"
    echo "$FUNCTION_CODE"
    exit 1
fi

# Check if the function already exists
if grep -q "function activate_labelmaker" "$PROFILE_FILE" 2>/dev/null; then
    echo "Function already exists in $PROFILE_FILE"
else
    echo "" >> "$PROFILE_FILE"
    echo "# LabelMaker auto-activation" >> "$PROFILE_FILE"
    echo "$FUNCTION_CODE" >> "$PROFILE_FILE"
    echo "Added auto-activation function to $PROFILE_FILE"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  labelmaker"
echo "  # or"
echo "  activate_labelmaker"
echo ""
echo "To reload your shell profile, run:"
echo "  source $PROFILE_FILE"
echo ""
echo "You can also use the provided scripts:"
echo "  ./run_app.sh      # Run the app with auto venv activation"
echo "  ./activate_venv.sh # Just activate the venv" 