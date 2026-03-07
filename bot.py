# ======================================================
# PREMIUM LOOK TELEGRAM FILE RENAME BOT
# ======================================================

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import time

# =========================
# BOT CONFIGURATION
# =========================

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "premium-rename-bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# =========================
# PROGRESS BAR FUNCTION
# =========================

async def progress(current, total, message, start, action):

    now = time.time()
    diff = now - start

    if diff < 1:
        return

    percentage = current * 100 / total
    speed = current / diff
    eta = round((total - current) / speed) if speed > 0 else 0

    bar_length = 20
    filled = int(bar_length * current // total)

    bar = "■" * filled + "□" * (bar_length - filled)

    try:
        await message.edit_text(
            f"{action}...\n\n"
            f"{bar}\n\n"
            f"📦 Size: {round(current/(1024*1024),2)}MB | {round(total/(1024*1024),2)}MB\n"
            f"⚡ Speed: {round(speed/1024,2)} KB/s\n"
            f"⏱ ETA: {eta}s"
        )
    except:
        pass


# ======================================================
# START MENU (PREMIUM STYLE)
# ======================================================

@app.on_message(filters.command("start"))
async def start(client, message):

    caption = (
        f"✨ **HEY! {message.from_user.first_name}**\n\n"
        "» I AM ADVANCED FILE RENAME BOT!\n"
        "I CAN AUTO RENAME FILES WITH CUSTOM CAPTION "
        "AND THUMBNAIL.\n\n"
        "**• MY ALL COMMANDS •**"
    )

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/YOUR_CHANNEL"),
                InlineKeyboardButton("🆘 Support", url="https://t.me/YOUR_GROUP")
            ],
            [
                InlineKeyboardButton("ℹ️ About", callback_data="about"),
                InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/ATF_Admin_Gojo")
            ]
        ]
    )

    await message.reply_photo(
        photo="https://i.imgur.com/Z6XK9Xg.jpeg",  # replace with your banner image
        caption=caption,
        reply_markup=buttons
    )


# ======================================================
# ABOUT BUTTON
# ======================================================

@app.on_callback_query(filters.regex("about"))
async def about(client, query):

    await query.message.edit_text(
        "🤖 **Advanced Rename Bot**\n\n"
        "Features:\n"
        "• Auto Rename Files\n"
        "• Custom Caption\n"
        "• Thumbnail Support\n"
        "• Fast Processing\n\n"
        "👨‍💻 Developer: @ATF_Admin_Gojo"
    )


# ======================================================
# FILE DETECTION
# ======================================================

@app.on_message(filters.document)
async def detect_file(client, message):

    file_name = message.document.file_name

    await message.reply_text(
        f"📂 **File Detected**\n\n"
        f"`{file_name}`\n\n"
        "✏️ Send the **new file name with extension**"
    )

    # Wait for new filename
    new_name_msg = await client.listen(message.chat.id)

    new_name = new_name_msg.text

    # ======================
    # DOWNLOAD FILE
    # ======================

    status = await message.reply_text("⬇ Starting download...")

    start = time.time()

    file_path = await message.download(
        progress=progress,
        progress_args=(status, start, "Downloading")
    )

    # ======================
    # RENAME FILE
    # ======================

    new_file = new_name

    os.rename(file_path, new_file)

    # ======================
    # UPLOAD FILE
    # ======================

    start = time.time()

    await message.reply_document(
        new_file,
        file_name=new_name,
        progress=progress,
        progress_args=(status, start, "Uploading")
    )

    # ======================
    # CLEAN TEMP FILE
    # ======================

    os.remove(new_file)

    await status.delete()


# ======================================================
# RUN BOT
# ======================================================

app.run()
