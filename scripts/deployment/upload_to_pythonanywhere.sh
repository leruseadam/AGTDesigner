#!/bin/bash
# PythonAnywhere Database Upload Script
# Generated: 2025-10-12 13:04:45

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         PythonAnywhere Database Upload Script                       ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
ZIP_FILE="database_sync_to_pythonanywhere_20251012_130445.zip"
DB_FILE="product_database.db"

# Check if zip file exists
if [ ! -f "$ZIP_FILE" ]; then
    echo "❌ Error: $ZIP_FILE not found!"
    exit 1
fi

echo "📦 Archive: $ZIP_FILE"
echo ""

# Prompt for username
read -p "Enter your PythonAnywhere username: " PA_USERNAME

if [ -z "$PA_USERNAME" ]; then
    echo "❌ Error: Username cannot be empty"
    exit 1
fi

echo ""
echo "🚀 Starting upload to PythonAnywhere..."
echo ""

# Upload via SCP
echo "Step 1: Uploading archive..."
scp "$ZIP_FILE" "$PA_USERNAME@ssh.pythonanywhere.com:~/"

if [ $? -ne 0 ]; then
    echo "❌ Upload failed!"
    exit 1
fi

echo "✅ Upload successful!"
echo ""
echo "Step 2: Extracting and moving files..."
echo ""

# SSH in and extract
ssh "$PA_USERNAME@ssh.pythonanywhere.com" << 'ENDSSH'
cd ~
echo "Unzipping archive..."
unzip -o database_sync_to_pythonanywhere_20251012_130445.zip

echo "Creating directories..."
mkdir -p uploads/backups

echo "Moving database files..."
mv product_database.db uploads/
mv backup_*.db uploads/backups/ 2>/dev/null || true

echo "Verifying database..."
python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('uploads/product_database.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    print(f"✓ Database integrity: {result[0]}")
    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"✓ Products: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM strains")
    print(f"✓ Strains: {cursor.fetchone()[0]}")
    conn.close()
    print("✅ Database verification complete!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
EOF

echo ""
echo "✅ Database sync complete!"
echo ""
echo "⚠️  IMPORTANT: Don't forget to reload your web app!"
echo "   Go to the Web tab and click the green 'Reload' button"
echo ""
ENDSSH

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║  Sync Complete! Remember to reload your web app on PythonAnywhere   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
