#!/bin/bash
echo "=================================="
echo "Watching for DOH changes in real-time"
echo "=================================="
echo ""
echo "Please change a DOH dropdown in your UI now..."
echo ""
tail -f app.log | grep --line-buffered -i "doh\|update-doh\|Baker"
