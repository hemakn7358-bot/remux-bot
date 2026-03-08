import os
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

OPENAI_KEY = os.environ.get("OPENAI_KEY")
PERPLEXITY_KEY = os.environ.get("PERPLEXITY_KEY")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

openai.api_key = OPENAI_KEY

app = Client(
    "multi_ai_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user_mode = {}

# ---------- START MENU ---------- #

@app.on_message(filters.command("start"))
async def start(client, message):

    keyboard = InlineKeyboardMarkup(
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
        "🤖 Multi AI Assistant\n\nSelect your AI model.",
        reply_markup=keyboard
    )

# ---------- AI SELECT ---------- #

@app.on_callback_query()
async def choose_ai(client, query):

    user_id = query.from_user.id
    mode = query.data

    user_mode[user_id] = mode

    await query.message.edit_text(
        f"✅ {mode.upper()} mode activated.\n\nNow send your question."
    )

# ---------- CHATGPT ---------- #

async def chatgpt(prompt):

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

# ---------- PERPLEXITY ---------- #

async def perplexity(prompt):

    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-small-online",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    r = requests.post(url, json=payload, headers=headers)
    data = r.json()

    return data["choices"][0]["message"]["content"]

# ---------- GEMINI ---------- #

async def gemini(prompt):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"

    payload = {
        "contents": [
            {"parts":[{"text": prompt}]}
        ]
    }

    r = requests.post(url, json=payload)
    data = r.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]

# ---------- AI CHAT ---------- #

@app.on_message(filters.text & ~filters.command())
async def ai_chat(client, message):

    user_id = message.from_user.id
    mode = user_mode.get(user_id)

    if not mode:
        return await message.reply_text(
            "⚠️ Please choose AI first using /start"
        )

    prompt = message.text

    msg = await message.reply_text("🤔 Thinking...")

    try:

        if mode == "chatgpt":
            answer = await chatgpt(prompt)

        elif mode == "perplexity":
            answer = await perplexity(prompt)

        elif mode == "gemini":
            answer = await gemini(prompt)

        else:
            answer = "AI mode error."

        await msg.edit_text(answer)

    except Exception as e:
        await msg.edit_text(f"Error:\n{e}")

app.run()
