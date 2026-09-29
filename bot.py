import asyncio
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
from config import BOT_TOKEN, DOWNLOAD_DIR, MAX_DOWNLOAD_MB
from keyboards import main_keyboard, speed_keyboard, quality_keyboard, compress_keyboard
from media import bass, black_white, change_speed, circle, compress, cut, duration, resize, square, to_mp3, run_ffmpeg, out_path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("media-converter")

def parse_time(value: str) -> float:
    value = value.strip().replace(",", ".")
    if re.fullmatch(r"\\d+(?:\\.\\d+)?", value):
        return float(value)
    parts = value.split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ValueError("Invalid time. Use seconds, MM:SS or HH:MM:SS.")

def media_suffix(name: str, is_video: bool) -> str:
    ext = Path(name or "").suffix.lower()
    return ext if ext and len(ext) <= 8 else (".mp4" if is_video else ".mp3")

async def download_message_media(message, user_id: int):
    item = message.video or message.audio or message.document or message.voice
    if not item:
        return None
    tg_file = await item.get_file()
    name = getattr(item, "file_name", None) or ("video.mp4" if message.video else "audio.mp3")
    is_video = bool(message.video)
    if message.document:
        is_video = (message.document.mime_type or "").startswith("video/")
    size = item.file_size or 0
    if size > MAX_DOWNLOAD_MB * 1024 * 1024:
        raise ValueError(f"File is larger than {MAX_DOWNLOAD_MB} MB.")
    user_dir = DOWNLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / f"input_{len(list(user_dir.iterdir()))}{media_suffix(name, is_video)}"
    await tg_file.download_to_drive(str(path))
    return str(path), is_video

async def send_result(message, path: str, as_document=False):
    try:
        if as_document:
            await message.reply_document(document=path)
        elif path.endswith(".mp3"):
            await message.reply_audio(audio=path)
        elif path.endswith(".webm"):
            await message.reply_video(video=path, supports_streaming=True)
        else:
            await message.reply_video(video=path, supports_streaming=True)
    finally:
        try: os.remove(path)
        except OSError: pass

async def process(update, context, action: str, value=None):
    src = context.user_data.get("media_path")
    if not src or not os.path.exists(src):
        await update.effective_message.reply_text("Media session expired. Please upload the file again.")
        return
    msg = update.effective_message
    await context.bot.send_chat_action(msg.chat_id, ChatAction.UPLOAD_DOCUMENT)
    try:
        if action == "mp3": out = await to_mp3(src)
        elif action in {"slow", "slowmo", "speed"}: out = await change_speed(src, float(value))
        elif action == "bass": out = await bass(src)
        elif action in {"cut", "trim"}: out = await cut(src, *value)
        elif action == "resize": out = await resize(src, int(value))
        elif action == "square": out = await square(src)
        elif action == "black": out = await black_white(src)
        elif action == "compress": out = await compress(src, value)
        elif action == "circle": out = await circle(src)
        else: raise ValueError("Unknown action.")
        await send_result(msg, out)
    except Exception as exc:
        log.exception("Processing failed")
        await msg.reply_text(f"❌ Processing failed:\n{str(exc)[:1200]}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Media Converter Bot\n\nSend a video, audio or MP3 file and choose an action.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Upload a video/audio file first.\n\n"
        "Speed supports presets, custom multiplier and target duration.\n"
        "Cut/Trim accepts start end, for example 00:30 01:45."
    )

async def on_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    try:
        result = await download_message_media(message, update.effective_user.id)
        if not result: return
        path, is_video = result
        pending = context.user_data.get("pending")

        if pending in {"avmix", "vmix"}:
            first = context.user_data.get("media_path")
            if not first:
                context.user_data["media_path"] = path
                await message.reply_text("First file saved. Now send the second media file.")
                return
            second = path
            out = out_path(".mp4")
            try:
                if pending == "avmix":
                    await run_ffmpeg(["-i", first, "-i", second, "-filter_complex",
                        "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[a]",
                        "-map", "0:v?", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", out])
                else:
                    await run_ffmpeg(["-i", first, "-i", second, "-filter_complex",
                        "[0:v][1:v]hstack=inputs=2[v]",
                        "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", out])
                await send_result(message, out)
            except Exception as exc:
                await message.reply_text(f"❌ Mix failed: {str(exc)[:1000]}")
            finally:
                context.user_data.pop("pending", None)
                for p in (first, second):
                    try: os.remove(p)
                    except OSError: pass
            return

        old = context.user_data.get("media_path")
        if old and old != path:
            try: os.remove(old)
            except OSError: pass
        context.user_data["media_path"] = path
        context.user_data["media_kind"] = "video" if is_video else "audio"
        d = duration(path)
        await message.reply_text(
            f"✅ File received{(' · ' + str(round(d, 1)) + 's') if d else ''}.\nChoose an action:",
            reply_markup=main_keyboard(context.user_data["media_kind"])
        )
    except Exception as exc:
        await message.reply_text(f"❌ Could not download that file: {str(exc)[:1000]}")

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "back":
        await q.edit_message_text("Choose an action:", reply_markup=main_keyboard(context.user_data.get("media_kind", "audio")))
        return

    if data in {"mp3", "bass", "square", "black", "circle", "doc"}:
        if data == "doc":
            src = context.user_data.get("media_path")
            if src: await send_result(q.message, src, as_document=True)
            return
        if data in {"square", "black", "circle"} and context.user_data.get("media_kind") != "video":
            await q.message.reply_text("That option is for video.")
            return
        await process(update, context, data)
        return

    if data in {"slow", "slowmo", "speed"}:
        await q.message.reply_text("Choose speed:", reply_markup=speed_keyboard(data))
        return

    if data.startswith(("slow:", "slowmo:", "speed:")):
        action, value = data.split(":", 1)
        if value == "custom":
            context.user_data["pending"] = action
            await q.message.reply_text("Send speed multiplier, e.g. 0.65 or 1.75.")
            return
        if value == "target":
            context.user_data["pending"] = action + ":target"
            await q.message.reply_text("Send target duration, e.g. 03:00.")
            return
        await process(update, context, action, float(value))
        return

    if data in {"cut", "trim"}:
        context.user_data["pending"] = data
        await q.message.reply_text("Send start end, e.g. 00:30 01:45.")
        return

    if data == "resize":
        await q.message.reply_text("Choose output height:", reply_markup=quality_keyboard())
        return
    if data.startswith("resize:"):
        await process(update, context, "resize", data.split(":", 1)[1])
        return

    if data == "compress":
        await q.message.reply_text("Choose compression:", reply_markup=compress_keyboard())
        return
    if data.startswith("compress:"):
        await process(update, context, "compress", data.split(":", 1)[1])
        return

    if data in {"avmix", "vmix"}:
        context.user_data["pending"] = data
        await q.message.reply_text("Send the second media file now.")
        return

async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = context.user_data.get("pending")
    text = (update.message.text or "").strip()
    if not pending:
        await update.message.reply_text("Upload a video/audio file first.")
        return
    try:
        if pending in {"cut", "trim"}:
            parts = text.split()
            if len(parts) != 2: raise ValueError("Send exactly two times: start end")
            start, end = parse_time(parts[0]), parse_time(parts[1])
            total = duration(context.user_data["media_path"])
            if start < 0 or end <= start or (total and end > total + 0.5): raise ValueError("Invalid range for this media.")
            context.user_data.pop("pending", None)
            await process(update, context, pending, (start, end))
            return
        if pending in {"slow", "slowmo", "speed"}:
            factor = float(text)
            if not 0.25 <= factor <= 4: raise ValueError("Speed must be between 0.25x and 4x.")
            context.user_data.pop("pending", None)
            await process(update, context, pending, factor)
            return
        if pending.endswith(":target"):
            action = pending.split(":", 1)[0]
            target = parse_time(text)
            current = duration(context.user_data["media_path"])
            if target <= 0 or current <= 0: raise ValueError("Could not determine duration.")
            factor = current / target
            if not 0.25 <= factor <= 4: raise ValueError(f"Calculated speed is {factor:.2f}x; supported range is 0.25x–4x.")
            context.user_data.pop("pending", None)
            await process(update, context, action, factor)
    except Exception as exc:
        await update.message.reply_text(f"❌ {str(exc)}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    media_filter = filters.VIDEO | filters.AUDIO | filters.Document.ALL | filters.VOICE
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(media_filter, on_media))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("Bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
