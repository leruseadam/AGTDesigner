#!/usr/bin/env python3
"""
Fix indentation error in app.py
"""

def fix_indentation():
    """Fix the indentation error in app.py."""
    
    print("🔧 Fixing indentation error in app.py...")
    
    with open('app.py', 'r') as f:
        lines = f.readlines()
    
    # Find and fix the problematic section
    fixed_lines = []
    skip_next_few = False
    skip_count = 0
    
    for i, line in enumerate(lines):
        if skip_next_few:
            skip_count += 1
            if skip_count >= 10:  # Skip the problematic PythonAnywhere config
                skip_next_few = False
                skip_count = 0
            continue
            
        # Check if this is the start of the problematic section
        if 'PythonAnywhere-specific upload configurations' in line:
            skip_next_few = True
            skip_count = 0
            continue
            
        # Fix the indentation of the development mode block
        if 'app.config[\'SEND_FILE_MAX_AGE_DEFAULT\'] = 0' in line and '    ' in line:
            # This line should be indented properly
            fixed_lines.append('        ' + line.lstrip())
        elif 'app.config[\'DEBUG\'] = True' in line and '        ' in line:
            # This line should be indented properly
            fixed_lines.append('        ' + line.lstrip())
        elif 'app.config[\'PROPAGATE_EXCEPTIONS\'] = True' in line and '        ' in line:
            # This line should be indented properly
            fixed_lines.append('        ' + line.lstrip())
        elif 'logging.info("Running in DEVELOPMENT mode' in line and '        ' in line:
            # This line should be indented properly
            fixed_lines.append('        ' + line.lstrip())
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open('app.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("✅ Fixed indentation error")

if __name__ == "__main__":
    fix_indentation() 