#!/bin/bash

# Database Backup Script for PythonAnywhere
# Run this before Git operations to protect your database

echo "🛡️  Creating database backup before Git operations..."

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Create backup directory if it doesn't exist
BACKUP_DIR="$HOME/database_backups"
mkdir -p "$BACKUP_DIR"

# Check if we're on PythonAnywhere
if [[ "$PYTHONANYWHERE_SITE" != "" ]] || [[ "$PYTHONANYWHERE_DOMAIN" != "" ]]; then
    echo "🌐 PythonAnywhere environment detected"
    PYTHONANYWHERE_MODE=true
else
    echo "💻 Local environment detected"
    PYTHONANYWHERE_MODE=false
fi

# Find database files to backup
DATABASE_FILES=()

# Check common database locations
if [ -f "$PROJECT_DIR/product_database.db" ]; then
    DATABASE_FILES+=("$PROJECT_DIR/product_database.db")
fi

if [ -f "$PROJECT_DIR/src/core/data/product_database.db" ]; then
    DATABASE_FILES+=("$PROJECT_DIR/src/core/data/product_database.db")
fi

if [ -f "$HOME/databases/product_database.db" ]; then
    DATABASE_FILES+=("$HOME/databases/product_database.db")
fi

# Check for any .db, .sqlite, or .sqlite3 files in the project
while IFS= read -r -d '' file; do
    DATABASE_FILES+=("$file")
done < <(find "$PROJECT_DIR" -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" -print0 2>/dev/null)

if [ ${#DATABASE_FILES[@]} -eq 0 ]; then
    echo "ℹ️  No database files found to backup"
    exit 0
fi

echo "📦 Found ${#DATABASE_FILES[@]} database file(s) to backup:"

# Backup each database file
for db_file in "${DATABASE_FILES[@]}"; do
    if [ -f "$db_file" ]; then
        # Get file size
        file_size=$(du -h "$db_file" | cut -f1)
        
        # Create timestamp
        timestamp=$(date +%Y%m%d_%H%M%S)
        
        # Create backup filename
        filename=$(basename "$db_file")
        backup_filename="${filename%.*}_backup_${timestamp}.${filename##*.}"
        backup_path="$BACKUP_DIR/$backup_filename"
        
        echo "  📋 Backing up: $db_file ($file_size) -> $backup_path"
        
        # Create backup
        if cp "$db_file" "$backup_path"; then
            echo "  ✅ Backup created successfully"
            
            # Verify backup
            if [ -f "$backup_path" ]; then
                backup_size=$(du -h "$backup_path" | cut -f1)
                echo "  🔍 Backup verified: $backup_path ($backup_size)"
            else
                echo "  ❌ Backup verification failed"
            fi
        else
            echo "  ❌ Backup failed for $db_file"
        fi
    fi
done

# Clean up old backups (keep last 10)
echo "🧹 Cleaning up old backups (keeping last 10)..."
cd "$BACKUP_DIR" || exit 1
ls -t *.db *.sqlite *.sqlite3 2>/dev/null | tail -n +11 | xargs -r rm -f

# Show backup summary
echo ""
echo "📊 Backup Summary:"
echo "  📁 Backup directory: $BACKUP_DIR"
echo "  📦 Total backups: $(ls -1 "$BACKUP_DIR"/*.db "$BACKUP_DIR"/*.sqlite "$BACKUP_DIR"/*.sqlite3 2>/dev/null | wc -l)"
echo "  💾 Total backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"

echo ""
echo "✅ Database backup complete!"
echo "🛡️  Your database is now protected from Git changes" 