#!/bin/bash
echo "🚀 Quick PythonAnywhere Git Reset Deployment"
echo "============================================"
cd ~/AGTDesigner && git fetch origin && git reset --hard origin/main && git log --oneline -1 && touch /var/www/www_agtpricetags_com_wsgi.py && echo "✅ Deployment complete! Visit https://www.agtpricetags.com" 