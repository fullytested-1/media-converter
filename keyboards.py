from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_keyboard(media_kind: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🎵 MP3", callback_data="mp3"), InlineKeyboardButton("🐌 Slow", callback_data="slow")],
        [InlineKeyboardButton("⚡ Speed", callback_data="speed"), InlineKeyboardButton("🔊 Bass", callback_data="bass")],
        [InlineKeyboardButton("✂️ Cut", callback_data="cut"), InlineKeyboardButton("📄 Document", callback_data="doc")],
        [InlineKeyboardButton("⬛ Square", callback_data="square"), InlineKeyboardButton("📐 Resize", callback_data="resize")],
        [InlineKeyboardButton("🗜 Compress", callback_data="compress"), InlineKeyboardButton("⏱ Trim", callback_data="trim")],
        [InlineKeyboardButton("⚫ Black & White", callback_data="black"), InlineKeyboardButton("🎚 AV Mix", callback_data="avmix")],
        [InlineKeyboardButton("🎞 V-Mix", callback_data="vmix"), InlineKeyboardButton("🐢 Slowmo", callback_data="slowmo")],
        [InlineKeyboardButton("⭕ Circle", callback_data="circle")],
    ]
    return InlineKeyboardMarkup(rows)

def speed_keyboard(prefix="speed"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("0.25x", callback_data=f"{prefix}:0.25"), InlineKeyboardButton("0.5x", callback_data=f"{prefix}:0.5")],
        [InlineKeyboardButton("0.75x", callback_data=f"{prefix}:0.75"), InlineKeyboardButton("1.25x", callback_data=f"{prefix}:1.25")],
        [InlineKeyboardButton("1.5x", callback_data=f"{prefix}:1.5"), InlineKeyboardButton("2x", callback_data=f"{prefix}:2")],
        [InlineKeyboardButton("✏️ Custom", callback_data=f"{prefix}:custom"), InlineKeyboardButton("⏱ Target duration", callback_data=f"{prefix}:target")],
    ])

def quality_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("480p", callback_data="resize:480"), InlineKeyboardButton("720p", callback_data="resize:720"), InlineKeyboardButton("1080p", callback_data="resize:1080")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")],
    ])

def compress_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Low", callback_data="compress:low"), InlineKeyboardButton("Medium", callback_data="compress:medium"), InlineKeyboardButton("High", callback_data="compress:high")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back")],
    ])
