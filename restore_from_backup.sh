#!/bin/bash
# Restore database from specific corrupted backup file on PythonAnywhere

echo "🔧 RESTORING DATABASE FROM BACKUP"
echo "=================================="

BACKUP_FILE="uploads/product_database_AGT_Bothell.db.corrupted.20251012_213432"
CURRENT_DB="uploads/product_database_AGT_Bothell.db"

echo "Backup file: $BACKUP_FILE"
echo "Target database: $CURRENT_DB"
echo ""

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    echo ""
    echo "Available backup files:"
    ls -la uploads/product_database_AGT_Bothell.db.corrupted.* 2>/dev/null || echo "No backup files found"
    exit 1
fi

# Check backup file size and integrity
echo "Checking backup file..."
backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
echo "Backup file size: $backup_size"

# Test if backup file is a valid SQLite database
if sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;" 2>/dev/null | grep -q "ok"; then
    echo "✅ Backup file integrity: OK"
    
    # Check product count in backup
    backup_count=$(sqlite3 "$BACKUP_FILE" "SELECT COUNT(*) FROM products;" 2>/dev/null)
    echo "Backup product count: $backup_count"
    
    if [ "$backup_count" -gt 1000 ]; then
        echo "✅ Backup has good number of products"
        
        # Create backup of current database
        if [ -f "$CURRENT_DB" ]; then
            timestamp=$(date +%Y%m%d_%H%M%S)
            backup_current="uploads/product_database_AGT_Bothell.db.current_backup.$timestamp"
            cp "$CURRENT_DB" "$backup_current"
            echo "✅ Backed up current database to: $backup_current"
        fi
        
        # Restore from backup
        echo "🔄 Restoring from backup..."
        cp "$BACKUP_FILE" "$CURRENT_DB"
        echo "✅ Database restored from backup"
        
        # Verify restoration
        new_count=$(sqlite3 "$CURRENT_DB" "SELECT COUNT(*) FROM products;" 2>/dev/null)
        new_size=$(du -h "$CURRENT_DB" | cut -f1)
        echo "✅ New database size: $new_size"
        echo "✅ New product count: $new_count"
        
        if [ "$new_count" -gt 1000 ]; then
            echo ""
            echo "🎉 SUCCESS! Database restored successfully"
            echo "📊 Restored $new_count products from backup"
        else
            echo "❌ Restoration failed - low product count"
        fi
        
    else
        echo "❌ Backup has very few products ($backup_count)"
        echo "This backup may not be useful"
    fi
    
else
    echo "❌ Backup file integrity check failed"
    echo "This backup file may be corrupted"
fi

echo ""
echo "=================================="
echo "📋 NEXT STEPS:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' for your web app"
echo "3. Wait 30-60 seconds"
echo "4. Visit https://www.agtpricetags.com"
echo "5. Check if database stats are correct"
echo "=================================="
