#!/bin/bash

# Script to install requirements one by one to identify the problematic package

echo "Installing packages one by one..."

packages=(
    "Flask==3.0.2"
    "pandas==2.2.1"
    "python-docx==1.1.0"
    "docxtpl==0.16.7"
    "docxcompose==1.4.0"
    "openpyxl==3.1.2"
    "Pillow==10.2.0"
    "python-dateutil==2.8.2"
    "watchdog>=2.1.6"
    "PyQt6>=6.4.0"
    "Werkzeug==3.0.1"
    "Jinja2==3.1.3"
    "itsdangerous==2.1.2"
    "click==8.1.7"
    "MarkupSafe==2.1.5"
    "numpy==1.26.4"
)

for package in "${packages[@]}"; do
    echo "Installing $package..."
    pip install "$package"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install $package"
        exit 1
    fi
    echo "Successfully installed $package"
    echo "---"
done

echo "All packages installed successfully!"
