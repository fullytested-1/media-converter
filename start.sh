#!/bin/sh
set -eu

: "${BOT_TOKEN:?BOT_TOKEN is required}"

# Voroa Web Service health endpoint.
# Telegram polling runs as the main process.
PORT="${PORT:-3000}"
python -c '
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/healthz"):
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *args):
        pass

ThreadingHTTPServer(("0.0.0.0", int(os.environ.get("PORT", "3000"))), Health).serve_forever()
' &

export BOT_API_BASE_URL="${BOT_API_BASE_URL:-https://api.telegram.org/bot}"
export BOT_API_FILE_URL="${BOT_API_FILE_URL:-https://api.telegram.org/file/bot}"
export BOT_API_LOCAL_MODE="0"
export MAX_DOWNLOAD_MB="${MAX_DOWNLOAD_MB:-50}"

echo "Starting Media Converter Bot..."
echo "Health server listening on port ${PORT}"
echo "Using Telegram cloud Bot API"

exec python bot.py
