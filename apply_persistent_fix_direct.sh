#!/bin/bash
# Apply persistent storage fix directly on PythonAnywhere
echo "Applying persistent storage fix directly..."

# First, pull the latest changes
echo "Pulling latest changes from Git..."
git pull

# Then run the persistent storage fix
echo "Running persistent storage fix..."
bash fix_persistent_storage.sh

echo "Persistent storage fix applied!"
echo "Upload should now work with data persistence through server restarts."
