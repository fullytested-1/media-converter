#!/bin/sh
set -eu

: "${BOT_TOKEN:?BOT_TOKEN is required}"
: "${API_ID:?API_ID is required}"
: "${API_HASH:?API_HASH is required}"

# Voroa Web Service health endpoint.
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

# Run Telegram's Local Bot API server for large-file support.
telegram-bot-api   --api-id="${API_ID}"   --api-hash="${API_HASH}"   --local   --http-ip-address=127.0.0.1   --http-port=8081   --dir=/var/lib/telegram-bot-api   --temp-dir=/tmp/telegram-bot-api   --verbosity=1 &

API="http://127.0.0.1:8081/bot${BOT_TOKEN}"

echo "Starting Local Telegram Bot API..."
READY=0
for i in $(seq 1 60); do
  if curl -fsS "${API}/getMe" >/dev/null 2>&1; then
    READY=1
    echo "Local Telegram Bot API is ready."
    break
  fi
  sleep 1
done

if [ "${READY}" != "1" ]; then
  echo "ERROR: Local Telegram Bot API did not become ready."
  exit 1
fi

# IMPORTANT: Do not call /logOut on the local server here.
# /logOut would immediately invalidate the token for this local session,
# causing python-telegram-bot to fail with: BadRequest: Logged out.

export BOT_API_BASE_URL="http://127.0.0.1:8081/bot"
export BOT_API_FILE_URL="http://127.0.0.1:8081/file/bot"
export BOT_API_LOCAL_MODE="1"
export MAX_DOWNLOAD_MB="${MAX_DOWNLOAD_MB:-2048}"

echo "Starting Media Converter Bot..."
echo "Health server listening on port ${PORT}"

exec python bot.py
