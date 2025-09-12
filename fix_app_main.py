#!/usr/bin/env python3
"""
Fix the app.py main section to work with Flask
"""

def fix_app_main():
    """Fix the app.py main section"""
    
    app_file = 'app.py'
    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found")
        return False
    
    # Read the current file
    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the main section
    old_main = '''if __name__ == '__main__':
    # Create and run the application
    label_maker = LabelMakerApp()
    label_maker.run()'''
    
    new_main = '''if __name__ == '__main__':
    # Create and run the Flask application
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=False)'''
    
    if old_main in content:
        content = content.replace(old_main, new_main)
        print("✅ Fixed app.py main section to use Flask")
    else:
        print("⚠️  Could not find the main section to fix")
    
    # Write the fixed content
    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Also fix the deployment version
    deployment_file = 'pythonanywhere_deployment/app.py'
    if os.path.exists(deployment_file):
        with open(deployment_file, 'r', encoding='utf-8') as f:
            deployment_content = f.read()
        
        if old_main in deployment_content:
            deployment_content = deployment_content.replace(old_main, new_main)
            with open(deployment_file, 'w', encoding='utf-8') as f:
                f.write(deployment_content)
            print("✅ Fixed deployment app.py main section")
    
    print("✅ App main section fixes applied!")
    return True

if __name__ == "__main__":
    import os
    fix_app_main()
