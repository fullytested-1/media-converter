#!/bin/sh
set -eu

: "${TELEGRAM_API_ID:?TELEGRAM_API_ID is required}"
: "${TELEGRAM_API_HASH:?TELEGRAM_API_HASH is required}"
: "${BOT_TOKEN:?BOT_TOKEN is required}"

telegram-bot-api \
  --api-id="${TELEGRAM_API_ID}" \
  --api-hash="${TELEGRAM_API_HASH}" \
  --local \
  --http-ip-address=127.0.0.1 \
  --http-port=8081 \
  --dir=/var/lib/telegram-bot-api \
  --temp-dir=/tmp/telegram-bot-api \
  --verbosity=1 &

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
