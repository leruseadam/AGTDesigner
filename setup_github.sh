#!/bin/bash

# Setup GitHub Repository for Label Maker
# This script helps you push your project to your existing AGTDesigner repository

echo "=== GitHub Repository Setup ==="

# Check if we have a Git repository
if [ ! -d ".git" ]; then
    echo "Error: Not a Git repository. Run 'git init' first."
    exit 1
fi

echo "✓ Git repository found"

# Check if we have commits
if ! git log --oneline -1 > /dev/null 2>&1; then
    echo "Error: No commits found. Run 'git add .' and 'git commit' first."
    exit 1
fi

echo "✓ Git commits found"

# Get GitHub username
echo ""
echo "Please enter your GitHub username:"
read GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "Error: GitHub username is required"
    exit 1
fi

echo "GitHub username: $GITHUB_USERNAME"

# Use existing AGTDesigner repository
REPO_NAME="AGTDesigner"

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "Remote 'origin' already exists:"
    git remote get-url origin
    echo ""
    echo "Do you want to update it to point to your AGTDesigner repository? (y/n)"
    read UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ] || [ "$UPDATE_REMOTE" = "Y" ]; then
        git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✓ Remote updated to AGTDesigner repository"
    else
        echo "Keeping existing remote"
    fi
else
    echo "Adding AGTDesigner repository as remote..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "✓ Remote added"
fi

# Set branch to main
git branch -M main

echo ""
echo "=== Repository Information ==="
echo "Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "Branch: main"
echo ""
echo "=== Next Steps ==="
echo "1. Make sure your AGTDesigner repository exists on GitHub"
echo "2. If you want to force push (overwrite existing content), run:"
echo "   git push -u origin main --force"
echo ""
echo "3. If you want to merge with existing content, run:"
echo "   git push -u origin main"
echo ""
echo "4. Then follow the deployment guide:"
echo "   cat github_deployment_guide.md"
echo ""
echo "Note: The deployment guide will clone from:"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git" 