# 🎬 Telegram Media Converter Bot

A Telegram bot for editing **video, audio and MP3** files with FFmpeg.

## Features

- 🎵 Video → MP3
- 🐌 Slow down
- ⚡ Speed up / slow down with custom multiplier
- ⏱ Change speed by target duration
- 🔊 Bass boost
- ✂️ Cut / Trim audio and video
- 📄 Send as Telegram document
- ⬛ Square video
- 📐 Resize video (480p / 720p / 1080p)
- 🗜 Compress video/audio
- ⚫ Black & white video
- 🎚 AV Mix (mix a second audio/media file)
- 🎞 V-Mix (side-by-side video mix)
- 🐢 Slowmo
- ⭕ Circular video

## Stack

- Python 3.12+
- python-telegram-bot
- FFmpeg / FFprobe

## Local setup

1. Install FFmpeg and make sure \`ffmpeg\` and \`ffprobe\` are available in PATH.
2. Create a virtual environment:
   \`\`\`bash
   python -m venv .venv
   source .venv/bin/activate
   \`\`\`
3. Install packages:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`
4. Copy \`.env.example\` to \`.env\`:
   \`\`\`bash
   cp .env.example .env
   \`\`\`
5. Put your BotFather token in \`.env\`:
   \`\`\`env
   BOT_TOKEN=YOUR_TOKEN_HERE
   \`\`\`
6. Start:
   \`\`\`bash
   python bot.py
   \`\`\`

**Never commit your real bot token.** \`.env\` is ignored by Git.

## Docker

\`\`\`bash
docker build -t media-converter .
docker run --rm --env-file .env media-converter
\`\`\`

## Speed controls

The bot supports presets from **0.25x to 2x**, custom speed, and target-duration conversion.

Example: if a 5-minute file needs to become 3 minutes, choose **Target duration** and send \`03:00\`. The bot calculates the required speed automatically.

## Cut / Trim

Send:

\`\`\`
00:30 01:45
\`\`\`

The bot returns the selected section. Seconds and HH:MM:SS are also accepted.

## Notes

Telegram bot file-size limits depend on the Telegram Bot API and your deployment. The bot also has an application-level \`MAX_DOWNLOAD_MB\` setting.
