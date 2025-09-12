#!/bin/bash
# Fix frontend timeout - add timeout to upload requests
echo "Fixing frontend upload timeout..."

# Create backup
cp /home/adamcordova/AGTDesigner/static/js/main.js /home/adamcordova/AGTDesigner/static/js/main.js.backup.$(date +%Y%m%d_%H%M%S)

# Add timeout to the upload request in main.js
echo "Adding timeout to upload requests..."
sed -i 's/const response = await fetch.*upload.*{/const controller = new AbortController();\n        const timeoutId = setTimeout(() => controller.abort(), 30000); \/\/ 30 second timeout\n        \n        const response = await fetch(\/upload, {\n            method: \/POST\/,\n            body: formData,\n            signal: controller.signal\n        });\n        \n        clearTimeout(timeoutId);/' /home/adamcordova/AGTDesigner/static/js/main.js

# Also add timeout to enhanced-ui.js
echo "Adding timeout to enhanced-ui.js..."
sed -i 's/const response = await fetch.*upload.*{/const controller = new AbortController();\n        const timeoutId = setTimeout(() => controller.abort(), 30000); \/\/ 30 second timeout\n        \n        const response = await fetch(\/upload, {\n            method: \/POST\/,\n            body: formData,\n            signal: controller.signal\n        });\n        \n        clearTimeout(timeoutId);/' /home/adamcordova/AGTDesigner/static/js/enhanced-ui.js

echo "Frontend timeout fix applied!"
echo "Upload requests will now timeout after 30 seconds instead of hanging indefinitely."
