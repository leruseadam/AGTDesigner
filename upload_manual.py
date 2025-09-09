#!/usr/bin/env python3
"""
Manual Upload Helper
Provides options for uploading the database archive
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

def find_manual_archive():
    """Find the manual upload archive."""
    current_dir = Path(".")
    pattern = "manual_database_upload_*.tar.gz"
    archives = list(current_dir.glob(pattern))
    
    if not archives:
        print("❌ No manual upload archive found!")
        return None
    
    # Get the most recent one
    archives.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return archives[0]

def show_upload_options():
    """Show manual upload options."""
    archive = find_manual_archive()
    if not archive:
        return
    
    file_size_mb = archive.stat().st_size / (1024 * 1024)
    
    print("Manual Database Upload Helper")
    print("=" * 35)
    print(f"Archive: {archive.name}")
    print(f"Size: {file_size_mb:.1f} MB")
    print(f"Created: {datetime.fromtimestamp(archive.stat().st_mtime)}")
    print()
    
    print("Upload Options:")
    print("1. Open PythonAnywhere File Manager")
    print("2. Copy file path to clipboard")
    print("3. Show SSH upload command")
    print("4. Open upload guide")
    print("5. Exit")
    print()
    
    while True:
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            open_pythonanywhere()
            break
        elif choice == "2":
            copy_path_to_clipboard(archive)
            break
        elif choice == "3":
            show_ssh_command(archive)
            break
        elif choice == "4":
            open_upload_guide()
            break
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")

def open_pythonanywhere():
    """Open PythonAnywhere in browser."""
    print("Opening PythonAnywhere...")
    webbrowser.open("https://www.pythonanywhere.com")
    print("✅ PythonAnywhere opened in browser")
    print("Navigate to Files tab and upload the archive")

def copy_path_to_clipboard(archive):
    """Copy file path to clipboard."""
    try:
        # Try to copy to clipboard
        if sys.platform == "darwin":  # macOS
            subprocess.run(["pbcopy"], input=str(archive.absolute()), text=True)
            print(f"✅ File path copied to clipboard: {archive.absolute()}")
        elif sys.platform == "linux":
            subprocess.run(["xclip", "-selection", "clipboard"], input=str(archive.absolute()), text=True)
            print(f"✅ File path copied to clipboard: {archive.absolute()}")
        else:
            print(f"File path: {archive.absolute()}")
            print("(Copy this path manually)")
    except:
        print(f"File path: {archive.absolute()}")
        print("(Copy this path manually)")

def show_ssh_command(archive):
    """Show SSH upload command."""
    print("\nSSH Upload Command:")
    print("=" * 25)
    print(f"scp {archive.absolute()} adamcordova@ssh.pythonanywhere.com:/home/adamcordova/AGTDesigner/")
    print()
    print("After upload, SSH to the server and run:")
    print("cd /home/adamcordova/AGTDesigner")
    print(f"tar -xzf {archive.name}")
    print(f"rm {archive.name}")

def open_upload_guide():
    """Open the upload guide."""
    guide_path = Path("MANUAL_UPLOAD_GUIDE.md")
    if guide_path.exists():
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(guide_path)])
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", str(guide_path)])
        else:
            print(f"Open: {guide_path.absolute()}")
        print("✅ Upload guide opened")
    else:
        print("❌ Upload guide not found")

def main():
    """Main function."""
    show_upload_options()

if __name__ == "__main__":
    main()
