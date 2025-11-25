#!/bin/bash
# Run this ONCE on PythonAnywhere to set up the gsync alias
# Usage: bash setup_pa_aliases.sh

echo "Setting up git aliases for PythonAnywhere..."

# Add alias to .bashrc if it doesn't exist
if ! grep -q "alias gsync=" ~/.bashrc 2>/dev/null; then
    echo "" >> ~/.bashrc
    echo "# Git sync alias - no more stashing!" >> ~/.bashrc
    echo "alias gsync='git fetch origin && git reset --hard origin/main && git clean -fd'" >> ~/.bashrc
    echo "✅ Added gsync alias to ~/.bashrc"
else
    echo "✅ gsync alias already exists in ~/.bashrc"
fi

# Also add it to current session
alias gsync='git fetch origin && git reset --hard origin/main && git clean -fd'

echo ""
echo "✅ Setup complete! You can now use:"
echo "   gsync    - Sync with GitHub (no stashing needed!)"
echo ""
echo "Note: If you're in a new terminal, run: source ~/.bashrc"
echo "Or just use: gsync (it's already active in this session)"










