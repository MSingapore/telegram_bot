import json
import random
import os
import asyncio
import uuid
from datetime import datetime
from gtts import gTTS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

from config import TOKEN

# 🌸 PERSONALIZATION
NAME = "Husaina"

progress_lock = asyncio.Lock()

# 💌 MESSAGES
SUCCESS = [f"✨ Perfect, {NAME}!", f"😊 That’s right, {NAME}!"]
FAIL = [f"Almost {NAME} 😊 it's: {{correct}}"]

# 📂 LOAD DATA
with open("words.json", "r", encoding="utf-8") as f:
    WORDS = json.load(f)

if not os.path.exists("progress.json"):
    with open("progress.json", "w") as f:
        json.dump({}, f)

with open("progress.json", "r") as f:
    PROGRESS = json.load(f)

async def save_progress():
    async with progress_lock:
        with open("progress.json", "w") as f:
            json.dump(PROGRESS, f, indent=2)

# 🔥 STREAK
def update_streak(user_id):
    today = datetime.now().date()

    if user_id not in PROGRESS:
        PROGRESS[user_id] = {"correct": 0, "total": 0, "streak": 0, "last_active": ""}

    last = PROGRESS[user_id]["last_active"]

    if last:
        last_date = datetime.strptime(last, "%Y-%m-%d").date()
        diff = (today - last_date).days
        PROGRESS[user_id]["streak"] = PROGRESS[user_id]["streak"] + 1 if diff == 1 else 1
    else:
        PROGRESS[user_id]["streak"] = 1

    PROGRESS[user_id]["last_active"] = str(today)

# 🔊 AUDIO
def generate_audio_file(text):
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    gTTS(text=text, lang="fr").save(filename)
    return filename

# 🎛 MAIN MENU
def main_menu():
    return ReplyKeyboardMarkup(
        [["📘 Word", "❓ Quiz"], ["📊 Progress"]],
        resize_keyboard=True
    )

# 🌸 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hi {NAME} 💛\n\nReady to learn something new today? 🌸",
        reply_markup=main_menu()
    )

# 📘 WORD
async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = random.choice(WORDS)

    await update.message.reply_text(
        f"🌸 Word for you\n\n{w['word']}\n🔊 {w['pronunciation']}\n💛 {w['meaning']}"
    )

    loop = asyncio.get_running_loop()
    file = await loop.run_in_executor(None, generate_audio_file, w["word"])

    try:
        with open(file, "rb") as f:
            await update.message.reply_audio(audio=f)
    finally:
        if os.path.exists(file):
            os.remove(file)

# ❓ QUIZ (BUTTONS)
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = random.choice(WORDS)
    wrong = random.sample(WORDS, 2)

    options = [w["word"], wrong[0]["word"], wrong[1]["word"]]
    random.shuffle(options)

    keyboard = [
        [InlineKeyboardButton(opt, callback_data=opt)] for opt in options
    ]

    context.user_data["answer"] = w["word"]

    await update.message.reply_text(
        f"What means \"{w['meaning']}\"? 😊",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ✅ BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.message.chat_id)
    selected = query.data
    correct = context.user_data.get("answer")

    if user_id not in PROGRESS:
        PROGRESS[user_id] = {"correct": 0, "total": 0, "streak": 0, "last_active": ""}

    PROGRESS[user_id]["total"] += 1

    if selected == correct:
        PROGRESS[user_id]["correct"] += 1
        await query.edit_message_text(random.choice(SUCCESS))
    else:
        await query.edit_message_text(random.choice(FAIL).format(correct=correct))

    update_streak(user_id)
    await save_progress()

# 📊 PROGRESS
async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    data = PROGRESS.get(user_id)

    if not data:
        await update.message.reply_text("Start learning first 🌸")
        return

    acc = (data["correct"] / data["total"]) * 100 if data["total"] else 0

    await update.message.reply_text(
        f"🔥 {data['streak']} day streak\n✨ {data['correct']} correct\n💛 {acc:.1f}% accuracy"
    )

# ⏰ DAILY
async def daily_message(app):
    for user_id in PROGRESS:
        try:
            await app.bot.send_message(chat_id=user_id, text="🌸 Good morning 💛")
        except:
            pass

# 🧠 INACTIVE
async def check_inactive(app):
    today = datetime.now().date()
    for user_id, data in PROGRESS.items():
        last = data.get("last_active")
        if not last:
            continue
        last_date = datetime.strptime(last, "%Y-%m-%d").date()
        if (today - last_date).days >= 2:
            try:
                await app.bot.send_message(chat_id=user_id, text="We miss you 💛")
            except:
                pass

# 🔄 TEXT HANDLER FOR BUTTON MENU
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📘 Word":
        await word(update, context)
    elif text == "❓ Quiz":
        await quiz(update, context)
    elif text == "📊 Progress":
        await progress(update, context)

# 🚀 MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    print("🌸 Bot running...")

    async def start_scheduler(app):
        scheduler = AsyncIOScheduler()
        scheduler.add_job(daily_message, "cron", hour=9, minute=0, args=[app])
        scheduler.add_job(check_inactive, "interval", hours=12, args=[app])
        scheduler.start()

    app.post_init = start_scheduler

    app.run_polling()