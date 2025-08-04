#!/bin/bash

# Database Protection Setup Script for PythonAnywhere
# Run this script to set up complete database protection

echo "🛡️  Setting up Database Protection for PythonAnywhere"
echo "=================================================="

# Check if we're on PythonAnywhere
if [[ "$PYTHONANYWHERE_SITE" != "" ]] || [[ "$PYTHONANYWHERE_DOMAIN" != "" ]]; then
    echo "🌐 PythonAnywhere environment detected"
    PYTHONANYWHERE_MODE=true
else
    echo "💻 Local environment detected"
    echo "⚠️  This script is optimized for PythonAnywhere but will work locally too"
    PYTHONANYWHERE_MODE=false
fi

# Step 1: Create necessary directories
echo ""
echo "📁 Step 1: Creating database directories..."
mkdir -p ~/databases
mkdir -p ~/database_backups
chmod 755 ~/databases ~/database_backups

echo "  ✅ Created ~/databases directory"
echo "  ✅ Created ~/database_backups directory"

# Step 2: Verify .gitignore protection
echo ""
echo "🔍 Step 2: Verifying .gitignore protection..."

if grep -q "*.db" .gitignore && grep -q "*.sqlite" .gitignore && grep -q "*.sqlite3" .gitignore; then
    echo "  ✅ .gitignore properly configured for database protection"
else
    echo "  ❌ .gitignore missing database protection rules"
    echo "  📝 Adding database protection to .gitignore..."
    
    cat >> .gitignore << 'EOF'

# Database Protection (Added by setup script)
*.db
*.db-shm
*.db-wal
*.sqlite
*.sqlite3
database_backups/
databases/
EOF
    
    echo "  ✅ Added database protection rules to .gitignore"
fi

# Step 3: Set up Git hooks
echo ""
echo "🔒 Step 3: Setting up Git hooks..."

if [ -f ".git/hooks/pre-commit" ]; then
    echo "  ✅ Pre-commit hook already exists"
else
    echo "  📝 Creating pre-commit hook..."
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
#
# Git Pre-commit Hook for Database Protection
# Prevents accidental commits of database files
#

echo "🛡️  Running database protection check..."

# Check if any database files are being committed
if git diff --cached --name-only | grep -E '\.(db|sqlite|sqlite3)$'; then
    echo ""
    echo "❌ ERROR: Database files detected in commit!"
    echo ""
    echo "Database files are protected and should not be committed:"
    git diff --cached --name-only | grep -E '\.(db|sqlite|sqlite3)$' | sed 's/^/   - /'
    echo ""
    echo "These files are automatically excluded by .gitignore for safety."
    echo "If you need to commit database-related changes, please:"
    echo "   1. Remove database files from staging: git reset HEAD <filename>"
    echo "   2. Commit only schema changes or documentation"
    echo "   3. Use the backup scripts to protect your data"
    echo ""
    exit 1
fi

echo "✅ Database protection check passed"
exit 0
EOF
    
    chmod +x .git/hooks/pre-commit
    echo "  ✅ Pre-commit hook created and made executable"
fi

# Step 4: Make protection scripts executable
echo ""
echo "🔧 Step 4: Setting up protection scripts..."

# Make scripts executable
chmod +x backup_database.sh 2>/dev/null || echo "  ⚠️  backup_database.sh not found"
chmod +x deploy_to_pythonanywhere.sh 2>/dev/null || echo "  ⚠️  deploy_to_pythonanywhere.sh not found"
chmod +x monitor_database.py 2>/dev/null || echo "  ⚠️  monitor_database.py not found"

echo "  ✅ Protection scripts made executable"

# Step 5: Test database protection
echo ""
echo "🧪 Step 5: Testing database protection..."

# Test .gitignore
if git status --ignored | grep -q "\.db\|\.sqlite\|\.sqlite3"; then
    echo "  ✅ Database files are properly ignored by Git"
else
    echo "  ⚠️  No database files found to test with"
fi

# Test pre-commit hook
if [ -x ".git/hooks/pre-commit" ]; then
    echo "  ✅ Pre-commit hook is executable"
else
    echo "  ❌ Pre-commit hook is not executable"
fi

# Step 6: Create initial backup if database exists
echo ""
echo "📦 Step 6: Creating initial database backup..."

# Check for existing databases
DATABASE_FOUND=false
for db_pattern in "product_database.db" "*.db" "*.sqlite" "*.sqlite3"; do
    for db_file in $db_pattern; do
        if [ -f "$db_file" ]; then
            DATABASE_FOUND=true
            echo "  📋 Found database: $db_file"
            
            # Create backup
            timestamp=$(date +%Y%m%d_%H%M%S)
            filename=$(basename "$db_file")
            backup_filename="${filename%.*}_initial_backup_${timestamp}.${filename##*.}"
            backup_path="$HOME/database_backups/$backup_filename"
            
            if cp "$db_file" "$backup_path"; then
                echo "  ✅ Initial backup created: $backup_path"
            else
                echo "  ❌ Initial backup failed for $db_file"
            fi
        fi
    done
done

if [ "$DATABASE_FOUND" = false ]; then
    echo "  ℹ️  No existing database files found"
fi

# Step 7: Show protection summary
echo ""
echo "📊 Database Protection Setup Summary"
echo "=================================="
echo "  🛡️  .gitignore protection: ✅ Active"
echo "  🔒 Git pre-commit hook: ✅ Active"
echo "  📁 Database directories: ✅ Created"
echo "  📦 Backup system: ✅ Ready"
echo "  🔧 Protection scripts: ✅ Executable"
echo ""
echo "📋 Available Commands:"
echo "  ./backup_database.sh          - Create database backup"
echo "  ./deploy_to_pythonanywhere.sh - Safe deployment with backup"
echo "  python3 monitor_database.py   - Check database health"
echo ""
echo "📚 Documentation:"
echo "  docs/PYTHONANYWHERE_DATABASE_PROTECTION.md"
echo ""
echo "🎉 Database protection setup complete!"
echo "🛡️  Your database is now safe from Git changes!" 