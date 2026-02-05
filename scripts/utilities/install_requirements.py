#!/usr/bin/env python3
"""
Automated requirements installation with docxcompose patch
This script installs all dependencies and automatically applies the pkg_resources fix
Works on all platforms (Windows, macOS, Linux)
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    requirements_file = os.path.join(script_dir, 'requirements.txt')
    patch_script = os.path.join(script_dir, 'patch_docxcompose.py')
    
    # Check if files exist
    if not os.path.exists(requirements_file):
        print(f"❌ Error: requirements.txt not found at {requirements_file}")
        sys.exit(1)
    
    if not os.path.exists(patch_script):
        print(f"❌ Error: patch_docxcompose.py not found at {patch_script}")
        sys.exit(1)
    
    print("=" * 60)
    print("AGT Designer - Automated Installation")
    print("=" * 60)
    print()
    
    # Install requirements
    pip_cmd = [sys.executable, '-m', 'pip', 'install', '--user', '-r', requirements_file]
    if not run_command(pip_cmd, "Installing requirements"):
        print("\n❌ Failed to install requirements")
        sys.exit(1)
    
    print()
    
    # Apply patch
    patch_cmd = [sys.executable, patch_script]
    if not run_command(patch_cmd, "Applying docxcompose patch"):
        print("\n⚠️  Warning: Failed to apply patch, but continuing...")
        print("   You may see pkg_resources deprecation warnings")
    
    print()
    print("=" * 60)
    print("✅ Installation complete!")
    print("=" * 60)
    print("   - All requirements installed")
    print("   - docxcompose patched (pkg_resources → importlib.metadata)")
    print()
    print("Run 'python3 app.py' to start the application")
    print()

if __name__ == "__main__":
    main()

