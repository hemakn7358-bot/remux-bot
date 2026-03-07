, action):

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

import os
import subprocess
import json
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

# ================= CONFIG ================= #

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

MODERATORS = [123456789]  # put your telegram user id

app = Client("mkv-remux-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ================= GLOBAL STORAGE ================= #

user_files = {}
user_tracks = {}
banner_path = "banner.jpg"

# ================= START COMMAND ================= #

@app.on_message(filters.command("start"))
async def start(client, message: Message):

    text = f"""
✨ HELLO {message.from_user.first_name}

MKV REMUX BOT

COMMANDS

/start_remux - detect mkv tracks
/add_track - add track
/remove_track - remove track
/extract_track - extract track
/proceed - remux container

Developer : @ATF_Admin_Gojo
"""

    if os.path.exists(banner_path):
        await message.reply_photo(banner_path, caption=text)
    else:
        await message.reply_text(text)

# ================= BANNER COMMAND ================= #

@app.on_message(filters.command("banner") & filters.user(MODERATORS))
async def set_banner(client, message):

    await message.reply_text("Send new banner image")

    banner = await client.listen(message.chat.id)

    if banner.photo:
        await banner.download("banner.jpg")
        await message.reply_text("Banner updated")

# ================= FILE DETECTION ================= #

@app.on_message(filters.document | filters.video)
async def detect_file(client, message: Message):

    file = await message.download()

    user_files[message.from_user.id] = file

    await message.reply_text(
        "File received\n\nUse /start_remux to analyze tracks"
    )

# ================= TRACK DETECTION ================= #

@app.on_message(filters.command("start_remux"))
async def detect_tracks(client, message):

    user = message.from_user.id

    if user not in user_files:
        return await message.reply_text("Send MKV file first")

    file = user_files[user]

    cmd = [
        "ffprobe",
        "-v","quiet",
        "-print_format","json",
        "-show_streams",
        file
    ]

    result = subprocess.check_output(cmd)

    data = json.loads(result)

    tracks = data["streams"]

    user_tracks[user] = tracks

    text = "Tracks found\n\n"

    for i, t in enumerate(tracks):

        text += f"{i} : {t['codec_type']} ({t.get('codec_name','')})\n"

    await message.reply_text(text)

# ================= REMOVE TRACK ================= #

@app.on_message(filters.command("remove_track"))
async def remove_track(client, message):

    await message.reply_text("Send track numbers to remove")

    reply = await client.listen(message.chat.id)

    numbers = reply.text.split()

    user = message.from_user.id

    tracks = user_tracks[user]

    keep = []

    for i,t in enumerate(tracks):

        if str(i) not in numbers:
            keep.append(i)

    user_tracks[user] = keep

    await message.reply_text("Tracks updated")

# ================= EXTRACT TRACK ================= #

@app.on_message(filters.command("extract_track"))
async def extract_track(client, message):

    await message.reply_text("Send track number")

    reply = await client.listen(message.chat.id)

    track = reply.text

    user = message.from_user.id

    file = user_files[user]

    output = f"track_{track}.bin"

    cmd = [
        "ffmpeg",
        "-i",file,
        "-map",f"0:{track}",
        "-c","copy",
        output
    ]

    subprocess.run(cmd)

    await message.reply_document(output)

# ================= ADD TRACK ================= #

@app.on_message(filters.command("add_track"))
async def add_track(client, message):

    await message.reply_text("Send track file")

    track = await client.listen(message.chat.id)

    path = await track.download()

    await message.reply_text(f"Track {path} saved (will add in remux)")

# ================= REMUX ================= #

@app.on_message(filters.command("proceed"))
async def remux(client, message):

    user = message.from_user.id

    if user not in user_files:
        return await message.reply_text("No file")

    input_file = user_files[user]

    await message.reply_text("Send output name")

    name = await client.listen(message.chat.id)

    output = name.text

    cmd = [
        "ffmpeg",
        "-i",input_file,
        "-map","0",
        "-c","copy",
        output
    ]

    subprocess.run(cmd)

    await message.reply_document(output)

# ================= RUN BOT ================= #

app.run()    start = time.time()

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
