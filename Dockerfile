FROM aiogram/telegram-bot-api:latest AS telegram_api

FROM python:3.12-alpine

RUN apk add --no-cache ffmpeg curl ca-certificates libstdc++ openssl

COPY --from=telegram_api /usr/local/bin/telegram-bot-api /usr/local/bin/telegram-bot-api

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x /app/start.sh && mkdir -p /var/lib/telegram-bot-api /tmp/telegram-bot-api

EXPOSE 8081
CMD ["/app/start.sh"]
