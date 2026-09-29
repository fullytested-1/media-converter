#!/bin/sh
set -eu

: "${TELEGRAM_API_ID:?TELEGRAM_API_ID is required}"
: "${TELEGRAM_API_HASH:?TELEGRAM_API_HASH is required}"
: "${BOT_TOKEN:?BOT_TOKEN is required}"

# Voroa Web Service health endpoint.
# The Telegram bot still runs as the main polling process.
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
' >/tmp/health-server.log 2>&1 &

telegram-bot-api   --api-id="${TELEGRAM_API_ID}"   --api-hash="${TELEGRAM_API_HASH}"   --local   --http-ip-address=127.0.0.1   --http-port=8081   --dir=/var/lib/telegram-bot-api   --temp-dir=/tmp/telegram-bot-api   --verbosity=1 &

API="http://127.0.0.1:8081/bot${BOT_TOKEN}"

for i in $(seq 1 60); do
  if curl -fsS "${API}/getMe" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

curl -fsS -X POST "${API}/logOut" >/dev/null 2>&1 || true

export BOT_API_BASE_URL="http://127.0.0.1:8081/bot"
export BOT_API_FILE_URL="http://127.0.0.1:8081/file/bot"
export BOT_API_LOCAL_MODE="1"
export MAX_DOWNLOAD_MB="2048"

exec python bot.py
