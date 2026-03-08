import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client(
    "ai_assistant_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# store selected AI model for each user
user_mode = {}

# ---------------- START MENU ---------------- #

@app.on_message(filters.command("start"))
async def start(client, message):

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🤖 ChatGPT", callback_data="chatgpt"),
                InlineKeyboardButton("🔎 Perplexity", callback_data="perplexity")
            ],
            [
                InlineKeyboardButton("💬 Gemini", callback_data="gemini")
            ]
        ]
    )

    await message.reply_text(
        "🤖 Multi AI Assistant\n\nChoose your AI model.",
        reply_markup=buttons
    )

# ---------------- AI SELECTION ---------------- #

@app.on_callback_query()
async def choose_ai(client, query):

    user_id = query.from_user.id
    mode = query.data

    user_mode[user_id] = mode

    await query.message.edit_text(
        f"✅ {mode.upper()} mode activated.\n\nYou can now chat normally."
    )

# ---------------- AI CHAT ---------------- #

@app.on_message(filters.text & ~filters.command)
async def ai_chat(client, message):

    try:
        user_id = message.from_user.id
        mode = user_mode.get(user_id)

        if not mode:
            return await message.reply_text(
                "Please select an AI first using /start"
            )

        user_text = message.text

        # placeholder reply
        reply = f"AI MODE: {mode}\n\nYou said:\n{user_text}"

        await message.reply_text(reply)

    except Exception as e:
        await message.reply_text(f"Error: {e}")

app.run()
