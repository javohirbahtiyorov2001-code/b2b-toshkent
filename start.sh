#!/bin/bash
# Start B2B automation: HTTP server + lead auto-sync watcher
cd "$(dirname "$0")"

echo "🚀 Starting B2B Automation..."

# Kill any existing server on 5055
lsof -ti:5055 | xargs kill -9 2>/dev/null

# Start lead watcher in background
python3 sync_leads.py &
WATCHER_PID=$!
echo "👁  Lead watcher started (PID $WATCHER_PID)"

# Start HTTP server
python3 -m http.server 5055 &
SERVER_PID=$!
echo "🌐 HTTP server started on http://localhost:5055 (PID $SERVER_PID)"

sleep 1
open http://localhost:5055/dashboard/
echo "✅ Dashboard opened"

# Keep both alive; kill both on Ctrl+C
trap "kill $WATCHER_PID $SERVER_PID 2>/dev/null; echo 'Stopped.'" INT TERM
wait
