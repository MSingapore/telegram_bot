"""
🌸 French Learning Bot — Full Duolingo-Style Experience
A love-crafted language tutor for Husaina 💛

Features:
  📘 Learn        — Flashcard-style word lessons
  ❓ Quiz         — MCQ: English meaning → French word
  🔄 Reverse      — MCQ: French word → English meaning
  📝 Type         — Type the French word yourself (with fuzzy tolerance + hint)
  📖 Fill         — Fill-in-the-blank sentence challenge
  🔊 Listen       — gTTS audio pronunciation
  🔍 Review       — SRS-based review of due words
  📊 Progress     — XP, streak, hearts, accuracy, daily goal
  🏆 Badges       — 17 achievement badges
  📚 Category     — 10 topic categories
  📖 Vocabulary   — Word stats per category
  📅 Word of Day  — A new French word every day
  💡 Grammar Tip  — Random French grammar tips
  🔄 Reset        — Reset progress with confirmation
  ⏰ Reminder     — Daily APScheduler nudge at 9 AM UTC
  💖 Spaced Rep   — SRS-based word scheduling
"""

import os
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
def run_web():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"🌸 Bot is running")

    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

import re
import json
import random
import hashlib
import asyncio
from datetime import datetime, timedelta
from io import BytesIO

from gtts import gTTS
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import TOKEN

# ═══════════════════════════════════════════════════════════
# 🌸 CONSTANTS
# ═══════════════════════════════════════════════════════════

LEARNER_NAME   = "Husaina"
WORDS_FILE     = "words.json"
PROGRESS_FILE  = "progress.json"


MAX_HEARTS        = 5
HEART_REGEN_HOURS = 4   # 1 heart regenerates every 4 hours
DAILY_GOAL        = 10  # exercises needed to complete daily goal

XP_LEARN   = 5
XP_CORRECT = 10
XP_STREAK  = 5
XP_GOAL    = 25

LEVEL_MAP = [
    (0,    "🌱 A1 · Beginner"),
    (100,  "🌿 A2 · Elementary"),
    (300,  "🌳 B1 · Intermediate"),
    (600,  "🔥 B2 · Upper Intermediate"),
    (1000, "⭐ C1 · Advanced"),
    (1500, "💎 C2 · Mastery"),
]

CATEGORIES = {
    "greetings": "👋 Greetings",
    "food":      "🍎 Food",
    "daily":     "🏠 Daily Life",
    "emotions":  "💝 Emotions",
    "travel":    "✈️ Travel",
    "family":    "👨‍👩‍👧 Family",
    "verbs":     "⚡ Verbs",
    "places":    "📍 Places",
    "shopping":  "🛍️ Shopping",
    "questions": "❓ Questions",
}

ACHIEVEMENTS = [
    ("first_correct",  "🥇 First Step",        "Got your first correct answer!"),
    ("streak_3",       "🔥 On Fire",            "Reached a 3-day streak!"),
    ("streak_7",       "🌟 Week Warrior",       "Reached a 7-day streak!"),
    ("streak_14",      "🌙 Fortnight",          "Reached a 14-day streak!"),
    ("streak_30",      "👑 Monthly Master",     "Reached a 30-day streak!"),
    ("xp_100",         "💚 Rising Star",        "Earned 100 XP!"),
    ("xp_500",         "💛 Gold Learner",       "Earned 500 XP!"),
    ("xp_1000",        "💜 Language Hero",      "Earned 1000 XP!"),
    ("words_10",       "📚 Word Collector",     "Practiced 10 unique words!"),
    ("words_50",       "📖 Vocab Builder",      "Practiced 50 unique words!"),
    ("words_100",      "🗺️ Explorer",           "Practiced 100 unique words!"),
    ("perfect_5",      "✨ Perfect Round",      "5 correct answers in a row!"),
    ("all_categories", "🌈 Polyglot",           "Studied all 10 categories!"),
    ("daily_goal_1",   "🎯 Goal Getter",        "Completed your first daily goal!"),
    ("typed_10",       "⌨️ Keyboard Master",    "Typed 10 correct answers!"),
    ("fill_5",         "✏️ Sentence Filler",    "Completed 5 fill-in-the-blank!"),
    ("reviewed_10",    "🔄 Review Champion",    "Reviewed 10 words via SRS!"),
]

MOTIVATIONAL = [
    "Tu es brillante, {n}! 🌸",
    "Keep shining, {n}! ✨",
    "French suits you perfectly! 💛",
    "Every word brings you closer! 🎯",
    "Je crois en toi, {n}! 💪",
    "You're amazing! 🌟",
    "One word at a time! 🌈",
    "La pratique rend parfait! 🎉",
    "I'm so proud of you, {n}! 🌺",
    "Magnifique! Simply magnifique! 🇫🇷",
]

GRAMMAR_TIPS = [
    "🇫🇷 *Gender Matters!*\nFrench nouns are masculine (*le/un*) or feminine (*la/une*).\nEx: *le livre* (the book), *la maison* (the house)",
    "🇫🇷 *Making Plurals*\nMost French nouns become plural by adding *\\-s* at the end.\nEx: *un ami* → *des amis*",
    "🇫🇷 *Être (To Be)*\nJe *suis* · Tu *es* · Il/Elle *est*\nNous *sommes* · Vous *êtes* · Ils *sont*",
    "🇫🇷 *Avoir (To Have)*\nJ'*ai* · Tu *as* · Il/Elle *a*\nNous *avons* · Vous *avez* · Ils *ont*",
    "🇫🇷 *Adjective Placement*\nAdjectives usually come *after* the noun in French.\nEx: *une robe rouge* (a red dress)",
    "🇫🇷 *Saying No*\n*Ne...pas* wraps around the verb to negate.\nEx: Je *ne* mange *pas* = I don't eat",
    "🇫🇷 *Tu vs Vous*\n*Tu* = informal (friends & family)\n*Vous* = formal (strangers) or plural (groups)\nWhen in doubt, use *vous*!",
    "🇫🇷 *Liaison*\nA silent final consonant is pronounced when followed by a vowel word.\nEx: *vous avez* → sounds like 'voo\\-za\\-vay'",
    "🇫🇷 *Partitive Articles*\n*Du / De la / Des* all mean 'some'.\nEx: *Je veux du pain* = I want some bread",
    "🇫🇷 *Regular \\-ER Verbs*\nRemove \\-er, then add: \\-e, \\-es, \\-e, \\-ons, \\-ez, \\-ent.\nEx: *parler* → je *parle*, nous *parlons*",
    "🇫🇷 *Question Words*\n*Qui* = Who · *Quoi* = What · *Où* = Where\n*Quand* = When · *Comment* = How · *Pourquoi* = Why",
    "🇫🇷 *French Accents*\n*é* = 'ay' · *è/ê* = 'eh' · *ç* = 's' · *â* = 'ah'\nAccents can even change meaning: *ou* (or) vs *où* (where)!",
]

# SRS review intervals in days (index = correct streak count)
SRS_INTERVALS = [1, 2, 4, 7, 14, 30]

# ═══════════════════════════════════════════════════════════
# 📦 DATA LOADING
# ═══════════════════════════════════════════════════════════

with open(WORDS_FILE, "r", encoding="utf-8") as _f:
    _raw_words = json.load(_f)

# Deduplicate words per category at load time
WORDS: dict = {}
for _lvl, _cats in _raw_words.items():
    WORDS[_lvl] = {}
    for _cat, _wlist in _cats.items():
        _seen: set = set()
        _deduped = []
        for _w in _wlist:
            if _w["word"] not in _seen:
                _seen.add(_w["word"])
                _deduped.append(_w)
        WORDS[_lvl][_cat] = _deduped

# Global word lookup: french_word -> full word dict
WORD_LOOKUP: dict = {}
for _cat_words in WORDS["beginner"].values():
    for _wd in _cat_words:
        WORD_LOOKUP.setdefault(_wd["word"], _wd)

if not os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "w") as _f:
        json.dump({}, _f)

with open(PROGRESS_FILE, "r") as _f:
    PROGRESS: dict = json.load(_f)

_lock = asyncio.Lock()


# ═══════════════════════════════════════════════════════════
# 💾 SAVE
# ═══════════════════════════════════════════════════════════

async def save():
    async with _lock:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(PROGRESS, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════
# 👤 USER INIT / SCHEMA MIGRATION
# ═══════════════════════════════════════════════════════════

def _fresh_user() -> dict:
    return {
        "xp": 0,
        "level": LEVEL_MAP[0][1],
        "hearts": MAX_HEARTS,
        "last_heart_time": "",
        "streak": 0,
        "last_active": "",
        "daily_done": 0,
        "goal_date": "",
        "category": "greetings",
        "words": {},              # word -> {correct, wrong, next_review}
        "achievements": [],
        "total_correct": 0,
        "total_wrong": 0,
        "consec_correct": 0,
        "studied_cats": [],
        "total_typed": 0,         # correct answers via Type mode
        "total_filled": 0,        # correct answers via Fill mode
        "total_reviewed": 0,      # correct answers via Review mode
        "total_daily_goals": 0,   # number of daily goals completed
    }


def init_user(uid: str):
    if uid not in PROGRESS:
        PROGRESS[uid] = _fresh_user()
        return
    # Migrate: fill in any missing keys from the new schema
    defaults = _fresh_user()
    for key, val in defaults.items():
        if key not in PROGRESS[uid]:
            PROGRESS[uid][key] = val


# ═══════════════════════════════════════════════════════════
# ❤️ HEARTS
# ═══════════════════════════════════════════════════════════

def _regen_hearts(uid: str):
    u = PROGRESS[uid]
    if u["hearts"] >= MAX_HEARTS:
        return
    last = u.get("last_heart_time", "")
    now = datetime.now()
    if last:
        elapsed_h = (now - datetime.fromisoformat(last)).total_seconds() / 3600
        gain = int(elapsed_h // HEART_REGEN_HOURS)
        if gain > 0:
            u["hearts"] = min(MAX_HEARTS, u["hearts"] + gain)
            u["last_heart_time"] = now.isoformat()
    else:
        u["last_heart_time"] = now.isoformat()


def _lose_heart(uid: str) -> bool:
    """Deduct one heart; returns True if hearts still remain."""
    _regen_hearts(uid)
    u = PROGRESS[uid]
    if u["hearts"] > 0:
        u["hearts"] -= 1
        if not u.get("last_heart_time"):
            u["last_heart_time"] = datetime.now().isoformat()
    return u["hearts"] > 0


def _hearts_bar(uid: str) -> str:
    h = PROGRESS[uid]["hearts"]
    return "❤️" * h + "🖤" * (MAX_HEARTS - h)


# ═══════════════════════════════════════════════════════════
# ⭐ XP & LEVEL
# ═══════════════════════════════════════════════════════════

def _calc_level(xp: int) -> str:
    level = LEVEL_MAP[0][1]
    for threshold, name in LEVEL_MAP:
        if xp >= threshold:
            level = name
        else:
            break
    return level


def _add_xp(uid: str, amount: int) -> bool:
    """Add XP; returns True if level changed."""
    u = PROGRESS[uid]
    old = u["level"]
    u["xp"] += amount
    u["level"] = _calc_level(u["xp"])
    return u["level"] != old


def _xp_to_next(xp: int) -> str:
    for thresh, _ in LEVEL_MAP:
        if xp < thresh:
            return f"{thresh - xp} XP to next level"
    return "Max level reached! 🏆"


# ═══════════════════════════════════════════════════════════
# 🔥 STREAK
# ═══════════════════════════════════════════════════════════

def _update_streak(uid: str):
    u = PROGRESS[uid]
    today = datetime.now().date()
    last = u.get("last_active", "")
    if last:
        last_d = datetime.strptime(last, "%Y-%m-%d").date()
        diff = (today - last_d).days
        if diff == 0:
            return          # already counted today
        elif diff == 1:
            u["streak"] += 1
        else:
            u["streak"] = 1  # streak broken
    else:
        u["streak"] = 1
    u["last_active"] = str(today)


# ═══════════════════════════════════════════════════════════
# 🎯 DAILY GOAL
# ═══════════════════════════════════════════════════════════

def _tick_daily(uid: str) -> bool:
    """Increment daily counter; returns True if goal just completed."""
    u = PROGRESS[uid]
    today = str(datetime.now().date())
    if u.get("goal_date") != today:
        u["daily_done"] = 0
        u["goal_date"] = today
    u["daily_done"] += 1
    if u["daily_done"] == DAILY_GOAL:
        u["total_daily_goals"] = u.get("total_daily_goals", 0) + 1
        return True
    return False


# ═══════════════════════════════════════════════════════════
# 🏆 ACHIEVEMENTS
# ═══════════════════════════════════════════════════════════

def _check_achievements(uid: str) -> list:
    u = PROGRESS[uid]
    already = set(u["achievements"])
    msgs = []
    checks = {
        "first_correct":  u["total_correct"] >= 1,
        "streak_3":       u["streak"] >= 3,
        "streak_7":       u["streak"] >= 7,
        "streak_14":      u["streak"] >= 14,
        "streak_30":      u["streak"] >= 30,
        "xp_100":         u["xp"] >= 100,
        "xp_500":         u["xp"] >= 500,
        "xp_1000":        u["xp"] >= 1000,
        "words_10":       len(u["words"]) >= 10,
        "words_50":       len(u["words"]) >= 50,
        "words_100":      len(u["words"]) >= 100,
        "perfect_5":      u.get("consec_correct", 0) >= 5,
        "all_categories": len(set(u.get("studied_cats", []))) >= len(CATEGORIES),
        "daily_goal_1":   u.get("total_daily_goals", 0) >= 1,
        "typed_10":       u.get("total_typed", 0) >= 10,
        "fill_5":         u.get("total_filled", 0) >= 5,
        "reviewed_10":    u.get("total_reviewed", 0) >= 10,
    }
    for aid, condition in checks.items():
        if condition and aid not in already:
            u["achievements"].append(aid)
            for a_id, a_name, a_desc in ACHIEVEMENTS:
                if a_id == aid:
                    msgs.append(f"🏆 *Achievement Unlocked!*\n*{a_name}*\n_{a_desc}_")
    return msgs


# ═══════════════════════════════════════════════════════════
# 📝 SPACED REPETITION
# ═══════════════════════════════════════════════════════════

def _update_memory(uid: str, word: str, correct: bool):
    u = PROGRESS[uid]
    today = str(datetime.now().date())
    if word not in u["words"]:
        u["words"][word] = {"correct": 0, "wrong": 0, "next_review": today}
    w = u["words"][word]
    if correct:
        w["correct"] += 1
        interval = SRS_INTERVALS[min(w["correct"] - 1, len(SRS_INTERVALS) - 1)]
        w["next_review"] = str((datetime.now() + timedelta(days=interval)).date())
    else:
        w["wrong"] += 1
        w["next_review"] = today  # review again today


# ═══════════════════════════════════════════════════════════
# 🧠 SMART WORD PICKER (SRS-aware)
# ═══════════════════════════════════════════════════════════

def _pick_word(uid: str) -> dict:
    u = PROGRESS[uid]
    words = WORDS["beginner"][u["category"]]
    today = datetime.now().date()

    # 1. Words due for review
    due = []
    for w in words:
        wdata = u["words"].get(w["word"])
        if wdata:
            rev_date = datetime.strptime(wdata["next_review"], "%Y-%m-%d").date()
            if rev_date <= today:
                due.append(w)
    if due:
        return random.choice(due)

    # 2. New words not yet seen
    seen = set(u["words"].keys())
    new = [w for w in words if w["word"] not in seen]
    if new:
        return new[0]

    # 3. Random fallback
    return random.choice(words)


def _wrong_word_options(correct_word: str, n: int = 3) -> list:
    pool = list({w["word"] for wl in WORDS["beginner"].values()
                 for w in wl if w["word"] != correct_word})
    return random.sample(pool, min(n, len(pool)))


def _wrong_meaning_options(correct_meaning: str, n: int = 3) -> list:
    pool = list({w["meaning"] for wl in WORDS["beginner"].values()
                 for w in wl if w["meaning"] != correct_meaning})
    return random.sample(pool, min(n, len(pool)))


def _motivational() -> str:
    return random.choice(MOTIVATIONAL).format(n=LEARNER_NAME)


# ═══════════════════════════════════════════════════════════
# 🎵 VOICE (gTTS)
# ═══════════════════════════════════════════════════════════

async def _send_voice_for_message(message, word: str):
    """Send French pronunciation audio; falls back to text on error."""
    try:
        tts = gTTS(text=word, lang="fr", slow=False)
        buf = BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        await message.reply_voice(voice=buf)
    except Exception:
        pron = WORD_LOOKUP.get(word, {}).get("pronunciation", "...")
        await message.reply_text(f"🔊 *{word}*  /{pron}/", parse_mode="Markdown")


# ═══════════════════════════════════════════════════════════
# 🖥️ KEYBOARDS
# ═══════════════════════════════════════════════════════════

MAIN_KB = ReplyKeyboardMarkup(
    [
        ["📘 Learn",   "❓ Quiz"],
        ["🔄 Reverse", "📝 Type"],
        ["📖 Fill",    "🔍 Review"],
        ["🔊 Listen",  "📊 Progress"],
        ["🏆 Badges",  "📚 Category"],
    ],
    resize_keyboard=True
)


def _category_kb() -> InlineKeyboardMarkup:
    items = list(CATEGORIES.items())
    rows = [
        [InlineKeyboardButton(v, callback_data=f"cat:{k}") for k, v in items[i:i+2]]
        for i in range(0, len(items), 2)
    ]
    return InlineKeyboardMarkup(rows)


def _lesson_kb(word: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔊 Hear it", callback_data=f"voice:{word}"),
        InlineKeyboardButton("Next ➡️",    callback_data="lesson:next"),
    ]])


def _quiz_kb(options: list, correct: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt, callback_data=f"Q:{correct}:{opt}")] for opt in options]
    )


def _rev_kb(options: list, word: str, correct_m: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt, callback_data=f"R:{word}:{correct_m}:{opt}")] for opt in options]
    )


def _review_quiz_kb(options: list, correct: str) -> InlineKeyboardMarkup:
    """Review-mode quiz keyboard (uses RV: prefix to track reviewed count)."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt, callback_data=f"RV:{correct}:{opt}")] for opt in options]
    )


def _type_kb(word: str) -> InlineKeyboardMarkup:
    """Inline keyboard for type/fill mode with a hint button."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("💡 Hint", callback_data=f"hint:{word}"),
    ]])


# ═══════════════════════════════════════════════════════════
# 📖 LESSON TEXT BUILDER
# ═══════════════════════════════════════════════════════════

def _lesson_card(w: dict, uid: str) -> str:
    cat = CATEGORIES[PROGRESS[uid]["category"]]
    example = w.get("example", "—").replace("{LEARNER_NAME}", LEARNER_NAME)
    return (
        f"📘 *Lesson · {cat}*\n\n"
        f"🇫🇷  *{w['word']}*\n"
        f"🇬🇧  _{w['meaning']}_\n"
        f"🔊  /{w['pronunciation']}/\n\n"
        f"📝  _{example}_\n\n"
        f"_{_motivational()}_\n\n"
        f"+{XP_LEARN} XP  ·  {_hearts_bar(uid)}"
    )


# ═══════════════════════════════════════════════════════════
# 🚀 /start
# ═══════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _update_streak(uid)
    await save()

    u = PROGRESS[uid]
    streak_line = (f"🔥 Day {u['streak']} streak — keep it up!\n\n"
                   if u["streak"] > 1 else "")

    await update.message.reply_text(
        f"*Bonjour, {LEARNER_NAME}!* 🌸\n\n"
        f"Your personal French tutor is here! 💛\n\n"
        f"{streak_line}"
        f"📘 *Learn*     — Flashcard word lessons\n"
        f"❓ *Quiz*      — Pick the French word\n"
        f"🔄 *Reverse*   — Pick the English meaning\n"
        f"📝 *Type*      — Spell it yourself\n"
        f"📖 *Fill*      — Complete a French sentence\n"
        f"🔍 *Review*    — Revise SRS-due words\n"
        f"🔊 *Listen*    — Hear the pronunciation\n"
        f"📊 *Progress*  — Your stats & daily goal\n"
        f"🏆 *Badges*    — 17 achievements to unlock\n"
        f"📚 *Category*  — 10 topics to explore\n\n"
        f"Commands: /wotd · /tip · /vocabulary · /reset · /help\n\n"
        f"Current category: *{CATEGORIES[u['category']]}*\n\n"
        f"_Allons-y! Let's go!_ 🚀",
        parse_mode="Markdown",
        reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# ❓ HELP
# ═══════════════════════════════════════════════════════════

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌸 *French Bot — Help*\n"
        f"{'─' * 28}\n\n"
        f"*Menu Buttons*\n"
        f"📘 Learn     — Study a new word (flashcard)\n"
        f"❓ Quiz      — MCQ: what is the French word?\n"
        f"🔄 Reverse   — MCQ: what does this mean?\n"
        f"📝 Type      — Type the French word yourself\n"
        f"📖 Fill      — Complete a sentence with the missing word\n"
        f"🔍 Review    — Practise words due for SRS review\n"
        f"🔊 Listen    — Hear the pronunciation (audio)\n"
        f"📊 Progress  — XP, streak, daily goal & stats\n"
        f"🏆 Badges    — All 17 achievements\n"
        f"📚 Category  — Switch between 10 topic categories\n\n"
        f"*Slash Commands*\n"
        f"/start       — Welcome screen\n"
        f"/wotd        — Word of the Day 📅\n"
        f"/tip         — Random French grammar tip 💡\n"
        f"/vocabulary  — Words practiced per category 📖\n"
        f"/reset       — Reset your progress (with confirmation)\n"
        f"/help        — This help message\n\n"
        f"_Bon courage, {LEARNER_NAME}!_ 💛",
        parse_mode="Markdown",
        reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# 📘 LEARN
# ═══════════════════════════════════════════════════════════

async def cmd_learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    w = _pick_word(uid)
    cat = PROGRESS[uid]["category"]

    # Track studied category for the "Polyglot" badge
    studied = PROGRESS[uid].setdefault("studied_cats", [])
    if cat not in studied:
        studied.append(cat)

    context.user_data["word"] = w
    context.user_data["mode"] = "learn"

    leveled = _add_xp(uid, XP_LEARN)
    _update_memory(uid, w["word"], True)
    await save()

    await update.message.reply_text(
        _lesson_card(w, uid),
        parse_mode="Markdown",
        reply_markup=_lesson_kb(w["word"])
    )

    if leveled:
        await update.message.reply_text(
            f"🎉 *Level Up!*  You're now *{PROGRESS[uid]['level']}*!\n"
            f"Incredible, {LEARNER_NAME}! 🌟",
            parse_mode="Markdown"
        )


# ═══════════════════════════════════════════════════════════
# ❓ QUIZ  (English meaning → French word)
# ═══════════════════════════════════════════════════════════

async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    if PROGRESS[uid]["hearts"] == 0:
        await update.message.reply_text(
            f"💔 No hearts left, {LEARNER_NAME}!\n"
            f"1 heart regenerates every {HEART_REGEN_HOURS} hours. 🌸",
            reply_markup=MAIN_KB
        )
        return

    w = _pick_word(uid)
    context.user_data["word"] = w
    context.user_data["mode"] = "quiz"

    opts = [w["word"]] + _wrong_word_options(w["word"])
    random.shuffle(opts)

    await update.message.reply_text(
        f"❓ *Quiz · {CATEGORIES[PROGRESS[uid]['category']]}*\n\n"
        f"Which is the French word for:\n\n"
        f"🇬🇧  *\"{w['meaning']}\"*\n\n"
        f"{_hearts_bar(uid)}",
        parse_mode="Markdown",
        reply_markup=_quiz_kb(opts, w["word"])
    )


# ═══════════════════════════════════════════════════════════
# 🔄 REVERSE QUIZ  (French word → English meaning)
# ═══════════════════════════════════════════════════════════

async def cmd_reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    if PROGRESS[uid]["hearts"] == 0:
        await update.message.reply_text(
            f"💔 No hearts left! Come back soon. 🌸", reply_markup=MAIN_KB
        )
        return

    w = _pick_word(uid)
    context.user_data["word"] = w
    context.user_data["mode"] = "reverse"

    opts = [w["meaning"]] + _wrong_meaning_options(w["meaning"])
    random.shuffle(opts)

    await update.message.reply_text(
        f"🔄 *Reverse Quiz · {CATEGORIES[PROGRESS[uid]['category']]}*\n\n"
        f"What does this mean?\n\n"
        f"🇫🇷  *\"{w['word']}\"*  /{w['pronunciation']}/\n\n"
        f"{_hearts_bar(uid)}",
        parse_mode="Markdown",
        reply_markup=_rev_kb(opts, w["word"], w["meaning"])
    )


# ═══════════════════════════════════════════════════════════
# 📝 TYPE ANSWER
# ═══════════════════════════════════════════════════════════

async def cmd_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    if PROGRESS[uid]["hearts"] == 0:
        await update.message.reply_text(
            f"💔 No hearts left! Rest and return. 🌸", reply_markup=MAIN_KB
        )
        return

    w = _pick_word(uid)
    context.user_data["word"] = w
    context.user_data["mode"] = "type"

    await update.message.reply_text(
        f"📝 *Type the French word for:*\n\n"
        f"🇬🇧  *\"{w['meaning']}\"*\n\n"
        f"Hint: /{w['pronunciation']}/\n\n"
        f"👇 Type your answer · Press 💡 for a letter hint\n"
        f"{_hearts_bar(uid)}",
        parse_mode="Markdown",
        reply_markup=_type_kb(w["word"])
    )


# ═══════════════════════════════════════════════════════════
# 📖 FILL-IN-THE-BLANK
# ═══════════════════════════════════════════════════════════

async def cmd_fill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    if PROGRESS[uid]["hearts"] == 0:
        await update.message.reply_text(
            f"💔 No hearts left! Come back soon. 🌸", reply_markup=MAIN_KB
        )
        return

    w = _pick_word(uid)
    context.user_data["word"] = w
    context.user_data["mode"] = "fill"

    sentence = w.get("example", "").replace("{LEARNER_NAME}", LEARNER_NAME)
    blanked = re.sub(re.escape(w["word"]), "____", sentence, count=1, flags=re.IGNORECASE)

    if blanked != sentence:
        prompt = (
            f"📖 *Fill in the Blank!*\n\n"
            f"Complete the French sentence:\n\n"
            f"_{blanked}_\n\n"
            f"🇬🇧 Clue: *\"{w['meaning']}\"*\n\n"
        )
    else:
        # Conjugated verb / multi-word — show sentence as context
        prompt = (
            f"📖 *Sentence Challenge!*\n\n"
            f"Read the sentence, then type the missing word:\n\n"
            f"_{sentence}_\n\n"
            f"🇬🇧 The key word means: *\"{w['meaning']}\"*\n\n"
        )

    prompt += f"👇 Type the French word · Press 💡 for a hint\n{_hearts_bar(uid)}"

    await update.message.reply_text(
        prompt,
        parse_mode="Markdown",
        reply_markup=_type_kb(w["word"])
    )


# ═══════════════════════════════════════════════════════════
# 🔍 REVIEW SESSION (SRS due words)
# ═══════════════════════════════════════════════════════════

async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    if PROGRESS[uid]["hearts"] == 0:
        await update.message.reply_text(
            f"💔 No hearts left! Come back after a rest. 🌸", reply_markup=MAIN_KB
        )
        return

    today = datetime.now().date()
    due = []
    for word_key, wdata in PROGRESS[uid]["words"].items():
        try:
            rev = datetime.strptime(wdata["next_review"], "%Y-%m-%d").date()
            if rev <= today:
                wd = WORD_LOOKUP.get(word_key)
                if wd:
                    due.append(wd)
        except (KeyError, ValueError):
            pass

    if not due:
        await update.message.reply_text(
            f"🎉 *Nothing to review today!*\n\n"
            f"All your words are fresh, {LEARNER_NAME}! 🌟\n"
            f"Keep practicing to grow your review queue.\n\n"
            f"💡 Tip: Use 📘 *Learn* to study new words!",
            parse_mode="Markdown",
            reply_markup=MAIN_KB
        )
        return

    # Present one due word as a quiz
    w = random.choice(due)
    context.user_data["word"] = w
    context.user_data["mode"] = "review"

    opts = [w["word"]] + _wrong_word_options(w["word"])
    random.shuffle(opts)

    remaining = len(due)
    await update.message.reply_text(
        f"🔍 *Review · {remaining} word{'s' if remaining > 1 else ''} due*\n\n"
        f"Which is the French word for:\n\n"
        f"🇬🇧  *\"{w['meaning']}\"*\n\n"
        f"{_hearts_bar(uid)}",
        parse_mode="Markdown",
        reply_markup=_review_quiz_kb(opts, w["word"])
    )


# ═══════════════════════════════════════════════════════════
# 🔊 LISTEN
# ═══════════════════════════════════════════════════════════

async def cmd_listen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)

    w = _pick_word(uid)
    await update.message.reply_text(
        f"🔊 *Pronunciation Practice*\n\n"
        f"🇫🇷  *{w['word']}*  =  _{w['meaning']}_\n"
        f"/{w['pronunciation']}/",
        parse_mode="Markdown"
    )
    await _send_voice_for_message(update.message, w["word"])


# ═══════════════════════════════════════════════════════════
# 📊 PROGRESS
# ═══════════════════════════════════════════════════════════

async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    _regen_hearts(uid)

    u = PROGRESS[uid]
    total_ans = u["total_correct"] + u["total_wrong"]
    accuracy  = f"{int(u['total_correct'] / total_ans * 100)}%" if total_ans else "—"

    today = str(datetime.now().date())
    done  = u["daily_done"] if u.get("goal_date") == today else 0
    bar   = "🟩" * min(done, DAILY_GOAL) + "⬜" * max(0, DAILY_GOAL - done)

    cats_studied = len(set(u.get("studied_cats", [])))

    # Count words due for review today
    today_dt = datetime.now().date()
    due_count = sum(
        1 for wdata in u["words"].values()
        if datetime.strptime(wdata["next_review"], "%Y-%m-%d").date() <= today_dt
    )

    await update.message.reply_text(
        f"📊 *{LEARNER_NAME}'s Progress*\n"
        f"{'─' * 28}\n"
        f"🏅  {u['level']}\n"
        f"⭐  {u['xp']} XP  ·  _{_xp_to_next(u['xp'])}_\n"
        f"🔥  {u['streak']}-day streak\n"
        f"{'─' * 28}\n"
        f"🎯  Daily Goal  ({done}/{DAILY_GOAL})\n"
        f"{bar}\n"
        f"{'─' * 28}\n"
        f"{_hearts_bar(uid)}  Hearts\n"
        f"📚  Words practiced:  {len(u['words'])}\n"
        f"🔍  Due for review:   {due_count}\n"
        f"✅  Correct:  {u['total_correct']}    ❌  Wrong:  {u['total_wrong']}\n"
        f"🎯  Accuracy:  {accuracy}\n"
        f"📂  Categories:  {cats_studied}/{len(CATEGORIES)}\n"
        f"{'─' * 28}\n"
        f"🏆  Badges:  {len(u['achievements'])}/{len(ACHIEVEMENTS)}\n\n"
        f"_{_motivational()}_",
        parse_mode="Markdown",
        reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# 🏆 BADGES
# ═══════════════════════════════════════════════════════════

async def cmd_badges(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)

    unlocked = set(PROGRESS[uid]["achievements"])
    lines = [f"🏆 *Badges  ({len(unlocked)}/{len(ACHIEVEMENTS)})*\n"]
    for aid, name, desc in ACHIEVEMENTS:
        icon = "✅" if aid in unlocked else "🔒"
        lines.append(f"{icon}  *{name}*  —  _{desc}_")

    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown", reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# 📚 CATEGORY SELECT
# ═══════════════════════════════════════════════════════════

async def cmd_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)
    cur = CATEGORIES[PROGRESS[uid]["category"]]
    await update.message.reply_text(
        f"📚 *Choose a Category*\n\nCurrent: *{cur}*\n\nSelect a topic to study:",
        parse_mode="Markdown",
        reply_markup=_category_kb()
    )


# ═══════════════════════════════════════════════════════════
# 📖 VOCABULARY (words per category)
# ═══════════════════════════════════════════════════════════

async def cmd_vocabulary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)

    u = PROGRESS[uid]
    practiced = set(u["words"].keys())

    lines = [f"📖 *{LEARNER_NAME}'s Vocabulary*\n{'─' * 26}\n"]
    total_practiced = 0
    total_words = 0

    for cat_key, cat_name in CATEGORIES.items():
        cat_words = WORDS["beginner"].get(cat_key, [])
        cat_total = len(cat_words)
        cat_done  = sum(1 for w in cat_words if w["word"] in practiced)
        total_practiced += cat_done
        total_words     += cat_total
        pct = int(cat_done / cat_total * 100) if cat_total else 0
        lines.append(f"{cat_name}:  *{cat_done}/{cat_total}*  ({pct}%)")

    lines.append(f"\n{'─' * 26}")
    lines.append(f"📊 Total: *{total_practiced}/{total_words}* words practiced")

    total_ans = u["total_correct"] + u["total_wrong"]
    acc = f"{int(u['total_correct'] / total_ans * 100)}%" if total_ans else "—"
    lines.append(f"🎯 Overall accuracy: *{acc}*")

    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown", reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# 💡 GRAMMAR TIP
# ═══════════════════════════════════════════════════════════

async def cmd_tip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tip = random.choice(GRAMMAR_TIPS)
    await update.message.reply_text(
        f"💡 *French Grammar Tip*\n\n{tip}\n\n_Bonne chance, {LEARNER_NAME}!_ 🌸",
        parse_mode="Markdown",
        reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# 📅 WORD OF THE DAY
# ═══════════════════════════════════════════════════════════

async def cmd_wotd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    init_user(uid)

    # Deterministic word selection from today's date
    today_str = str(datetime.now().date())
    all_words  = list(WORD_LOOKUP.values())
    seed_int   = int(hashlib.md5(today_str.encode()).hexdigest(), 16)
    w = all_words[seed_int % len(all_words)]
    example = w.get("example", "—").replace("{LEARNER_NAME}", LEARNER_NAME)

    await update.message.reply_text(
        f"📅 *Word of the Day*  —  _{today_str}_\n\n"
        f"🇫🇷  *{w['word']}*\n"
        f"🇬🇧  _{w['meaning']}_\n"
        f"🔊  /{w['pronunciation']}/\n\n"
        f"📝  _{example}_\n\n"
        f"_Un nouveau mot chaque jour!_ 🌸",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔊 Hear it", callback_data=f"voice:{w['word']}")
        ]])
    )


# ═══════════════════════════════════════════════════════════
# 🔄 RESET PROGRESS
# ═══════════════════════════════════════════════════════════

async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⚠️ *Reset Progress?*\n\n"
        f"This will permanently delete ALL your XP, streak, badges, and word history.\n\n"
        f"Are you sure?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Yes, reset",  callback_data="reset:confirm"),
            InlineKeyboardButton("❌ No, cancel",  callback_data="reset:cancel"),
        ]])
    )


# ═══════════════════════════════════════════════════════════
# ✏️ SHARED TYPED-ANSWER HANDLER (type & fill modes)
# ═══════════════════════════════════════════════════════════

async def _handle_typed_answer(update, uid: str, w: dict,
                               text: str, mode: str, context):
    context.user_data["mode"] = ""
    correct    = w["word"].lower().strip()
    typed      = text.lower().strip()
    is_right   = typed == correct
    fuzzy_note = ""

    # Allow 1-character typo for words longer than 4 chars
    if not is_right and len(correct) > 4:
        diff = (sum(a != b for a, b in zip(typed, correct))
                + abs(len(typed) - len(correct)))
        if diff == 1:
            is_right   = True
            fuzzy_note = f" _(almost! exact: *{w['word']}*)_"

    u = PROGRESS[uid]
    if is_right:
        u["total_correct"] += 1
        u["consec_correct"] = u.get("consec_correct", 0) + 1
        if mode == "type":
            u["total_typed"] = u.get("total_typed", 0) + 1
        elif mode == "fill":
            u["total_filled"] = u.get("total_filled", 0) + 1

        leveled   = _add_xp(uid, XP_CORRECT)
        goal_done = _tick_daily(uid)
        _update_streak(uid)
        _update_memory(uid, w["word"], True)
        ach_msgs  = _check_achievements(uid)
        await save()

        await update.message.reply_text(
            f"✅ *Correct!*{fuzzy_note}  +{XP_CORRECT} XP\n"
            f"🇫🇷 *{w['word']}* = _{w['meaning']}_\n\n"
            f"{_hearts_bar(uid)}  ·  ⭐ {u['xp']} XP",
            parse_mode="Markdown",
            reply_markup=MAIN_KB
        )
        if leveled:
            await update.message.reply_text(
                f"🎉 *Level Up!* You're now *{u['level']}*! 🌟",
                parse_mode="Markdown"
            )
        if goal_done:
            _add_xp(uid, XP_GOAL)
            await update.message.reply_text(
                f"🎯 *Daily Goal Complete!*  +{XP_GOAL} Bonus XP!\n"
                f"Amazing, {LEARNER_NAME}! 🏆🌸",
                parse_mode="Markdown"
            )
        for am in ach_msgs:
            await update.message.reply_text(am, parse_mode="Markdown")
    else:
        u["total_wrong"] = u.get("total_wrong", 0) + 1
        u["consec_correct"] = 0
        _lose_heart(uid)
        _update_memory(uid, w["word"], False)
        await save()

        await update.message.reply_text(
            f"❌ *Not quite!*\n"
            f"You typed: _{text}_\n"
            f"Correct:   *{w['word']}*\n\n"
            f"{_hearts_bar(uid)}  💔",
            parse_mode="Markdown",
            reply_markup=MAIN_KB
        )


# ═══════════════════════════════════════════════════════════
# 🔘 CALLBACK QUERY HANDLER
# ═══════════════════════════════════════════════════════════

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid  = str(q.message.chat_id)
    data = q.data
    init_user(uid)

    # ── Category switch ──────────────────────────────────
    if data.startswith("cat:"):
        cat = data[4:]
        PROGRESS[uid]["category"] = cat
        await save()
        await q.edit_message_text(
            f"✅  Switched to *{CATEGORIES[cat]}*!\n\nUse 📘 Learn or ❓ Quiz to start!",
            parse_mode="Markdown"
        )
        return

    # ── Voice from lesson card / WOTD ───────────────────
    if data.startswith("voice:"):
        word = data[6:]
        await _send_voice_for_message(q.message, word)
        return

    # ── Next lesson card ─────────────────────────────────
    if data == "lesson:next":
        _regen_hearts(uid)
        w   = _pick_word(uid)
        cat = PROGRESS[uid]["category"]
        studied = PROGRESS[uid].setdefault("studied_cats", [])
        if cat not in studied:
            studied.append(cat)
        context.user_data["word"] = w
        leveled = _add_xp(uid, XP_LEARN)
        _update_memory(uid, w["word"], True)
        await save()

        await q.message.reply_text(
            _lesson_card(w, uid),
            parse_mode="Markdown",
            reply_markup=_lesson_kb(w["word"])
        )
        if leveled:
            await q.message.reply_text(
                f"🎉 *Level Up!* You're now *{PROGRESS[uid]['level']}*! 🌟",
                parse_mode="Markdown"
            )
        return

    # ── Hint for Type / Fill ──────────────────────────────
    if data.startswith("hint:"):
        word = data[5:]
        if len(word) <= 2:
            hint_text = word[0] + "_" * (len(word) - 1)
        elif len(word) <= 5:
            hint_text = word[0] + "_" * (len(word) - 1)
        else:
            hint_text = word[:2] + "_" * (len(word) - 2)
        # Show as popup alert — no extra message clutter
        await q.answer(
            f"💡 Hint: {hint_text}  ({len(word)} letters)",
            show_alert=True
        )
        return

    # ── Reset confirmation ───────────────────────────────
    if data == "reset:confirm":
        if uid in PROGRESS:
            del PROGRESS[uid]
        init_user(uid)
        await save()
        await q.edit_message_text(
            f"✅ Progress reset! Fresh start, {LEARNER_NAME}! 🌸\n\n"
            f"Use /start to begin your journey again.",
            parse_mode="Markdown"
        )
        return

    if data == "reset:cancel":
        await q.edit_message_text(
            f"😊 Phew! Your progress is safe.\nKeep learning! 💪"
        )
        return

    # ── Quiz answer: Q:{correct_word}:{selected_word} ────
    if data.startswith("Q:"):
        parts      = data.split(":", 2)
        correct_w  = parts[1]
        selected_w = parts[2]
        is_right   = correct_w == selected_w
        wd         = WORD_LOOKUP.get(correct_w, {})
        display    = f"🇫🇷 *{correct_w}* = _{wd.get('meaning', '?')}_"
        await _process_answer(q, uid, correct_w, is_right, display, context)
        return

    # ── Reverse answer: R:{word}:{correct_m}:{selected_m} ──
    if data.startswith("R:"):
        parts      = data.split(":", 3)
        word       = parts[1]
        correct_m  = parts[2]
        selected_m = parts[3]
        is_right   = correct_m == selected_m
        display    = f"🇫🇷 *{word}* = _{correct_m}_"
        await _process_answer(q, uid, word, is_right, display, context)
        return

    # ── Review quiz answer: RV:{correct_word}:{selected_word} ──
    if data.startswith("RV:"):
        parts      = data.split(":", 2)
        correct_w  = parts[1]
        selected_w = parts[2]
        is_right   = correct_w == selected_w
        wd         = WORD_LOOKUP.get(correct_w, {})
        display    = f"🇫🇷 *{correct_w}* = _{wd.get('meaning', '?')}_"

        # Track review count for achievement
        if is_right:
            PROGRESS[uid]["total_reviewed"] = PROGRESS[uid].get("total_reviewed", 0) + 1

        await _process_answer(q, uid, correct_w, is_right, display, context)
        return


# ═══════════════════════════════════════════════════════════
# 🎯 SHARED ANSWER PROCESSOR (Quiz & Reverse)
# ═══════════════════════════════════════════════════════════

async def _process_answer(q, uid: str, word_key: str,
                          is_right: bool, display: str, context):
    u           = PROGRESS[uid]
    leveled     = False
    goal_done   = False
    ach_msgs    = []

    if is_right:
        u["total_correct"] += 1
        u["consec_correct"] = u.get("consec_correct", 0) + 1
        leveled   = _add_xp(uid, XP_CORRECT)
        goal_done = _tick_daily(uid)
        _update_streak(uid)
        _update_memory(uid, word_key, True)

        streak_bonus = ""
        if u["streak"] > 1:
            _add_xp(uid, XP_STREAK)
            streak_bonus = f"\n🔥 +{XP_STREAK} Streak Bonus!"

        msg = (
            f"✅ *Correct!*  +{XP_CORRECT} XP{streak_bonus}\n"
            f"{display}\n\n"
            f"{_hearts_bar(uid)}  ·  ⭐ {u['xp']} XP"
        )
        ach_msgs = _check_achievements(uid)
    else:
        u["total_wrong"] = u.get("total_wrong", 0) + 1
        u["consec_correct"] = 0
        _lose_heart(uid)
        _update_streak(uid)
        _update_memory(uid, word_key, False)

        msg = (
            f"❌ *Wrong!*\n"
            f"Correct: {display}\n\n"
            f"{_hearts_bar(uid)}  💔"
        )
        if u["hearts"] == 0:
            msg += f"\n\n💔 No hearts left! Rest a bit, {LEARNER_NAME}. 🌸"

    await q.edit_message_text(msg, parse_mode="Markdown")

    if leveled:
        await q.message.reply_text(
            f"🎉 *Level Up!* You're now *{u['level']}*! 🌟",
            parse_mode="Markdown"
        )
    if goal_done:
        _add_xp(uid, XP_GOAL)
        await q.message.reply_text(
            f"🎯 *Daily Goal Complete!*  +{XP_GOAL} Bonus XP!\n"
            f"Amazing work today, {LEARNER_NAME}! 🏆🌸",
            parse_mode="Markdown"
        )
    for am in ach_msgs:
        await q.message.reply_text(am, parse_mode="Markdown")

    await save()


# ═══════════════════════════════════════════════════════════
# 💬 TEXT / TYPE-ANSWER HANDLER
# ═══════════════════════════════════════════════════════════

MENU_MAP = {
    "📘 Learn":    cmd_learn,
    "❓ Quiz":     cmd_quiz,
    "🔄 Reverse":  cmd_reverse,
    "📝 Type":     cmd_type,
    "📖 Fill":     cmd_fill,
    "🔍 Review":   cmd_review,
    "🔊 Listen":   cmd_listen,
    "📊 Progress": cmd_progress,
    "🏆 Badges":   cmd_badges,
    "📚 Category": cmd_category,
}


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = str(update.effective_user.id)
    text = update.message.text.strip()
    init_user(uid)

    # Handle main menu buttons (clears any active session)
    if text in MENU_MAP:
        context.user_data["mode"] = ""
        await MENU_MAP[text](update, context)
        return

    # Handle typed / fill-in-the-blank answers
    mode = context.user_data.get("mode", "")
    if mode in ("type", "fill"):
        w = context.user_data.get("word")
        if not w:
            await update.message.reply_text(
                "Start a new exercise from the menu.", reply_markup=MAIN_KB
            )
            return
        await _handle_typed_answer(update, uid, w, text, mode, context)
        return

    # 💖 Heart renewal — Husaina sends "I LOVE YOU(UUU...)" to forward to engineer & refill hearts
    if re.fullmatch(r"i\s+love\s+you+[!💖💕❤️🥰😍✨🌸]*", text, re.IGNORECASE):
        PROGRESS[uid]["hearts"] = MAX_HEARTS
        PROGRESS[uid]["last_heart_time"] = ""
        await save()
        # Forward the love message to the engineer
        try:
            await context.bot.send_message(
                chat_id=1149671319,
                text=f"💌 *{LEARNER_NAME} says:*\n\n_{text}_ 💖🌸",
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await update.message.reply_text(
            f"💖 *Message sent!* 🥰\n\n"
            f"Your hearts have been fully restored as a reward!\n"
            f"{_hearts_bar(uid)}\n\n"
            f"_Now go show French who's boss!_ 🇫🇷✨",
            parse_mode="Markdown",
            reply_markup=MAIN_KB
        )
        return

    # Default nudge
    await update.message.reply_text(
        f"Use the menu buttons below, {LEARNER_NAME}! 🌸\n"
        f"Or type /help to see all commands.",
        reply_markup=MAIN_KB
    )


# ═══════════════════════════════════════════════════════════
# ⏰ DAILY REMINDER  (APScheduler)
# ═══════════════════════════════════════════════════════════

_scheduler = AsyncIOScheduler(timezone="UTC")


async def _on_startup(app):
    """Start the scheduler once the event loop is running."""
    _scheduler.add_job(_send_daily_reminders, "cron", hour=9, minute=0, args=[app])
    _scheduler.start()


async def _on_shutdown(app):
    """Cleanly stop the scheduler on exit."""
    if _scheduler.running:
        _scheduler.shutdown()


async def _send_daily_reminders(app):
    today = str(datetime.now().date())
    for uid, u in PROGRESS.items():
        if u.get("goal_date") != today or u.get("daily_done", 0) < DAILY_GOAL:
            try:
                streak = u.get("streak", 0)
                await app.bot.send_message(
                    chat_id=int(uid),
                    text=(
                        f"🌸 *Bonjour, {LEARNER_NAME}!*\n\n"
                        f"Time for your daily French practice! 🇫🇷\n"
                        + (f"🔥 {streak}-day streak to protect!\n" if streak
                           else "Start your streak today!\n")
                        + f"\n_Même cinq minutes suffisent! Even 5 minutes counts!_ 💛"
                    ),
                    parse_mode="Markdown"
                )
            except Exception:
                pass  # user may have blocked the bot


# ═══════════════════════════════════════════════════════════
# 🤖 MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(_on_startup)
        .post_shutdown(_on_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("help",       cmd_help))
    app.add_handler(CommandHandler("learn",      cmd_learn))
    app.add_handler(CommandHandler("quiz",       cmd_quiz))
    app.add_handler(CommandHandler("reverse",    cmd_reverse))
    app.add_handler(CommandHandler("type",       cmd_type))
    app.add_handler(CommandHandler("fill",       cmd_fill))
    app.add_handler(CommandHandler("listen",     cmd_listen))
    app.add_handler(CommandHandler("review",     cmd_review))
    app.add_handler(CommandHandler("progress",   cmd_progress))
    app.add_handler(CommandHandler("badges",     cmd_badges))
    app.add_handler(CommandHandler("category",   cmd_category))
    app.add_handler(CommandHandler("tip",        cmd_tip))
    app.add_handler(CommandHandler("wotd",       cmd_wotd))
    app.add_handler(CommandHandler("vocabulary", cmd_vocabulary))
    app.add_handler(CommandHandler("reset",      cmd_reset))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))

    print("🌸 French Learning Bot is running...")
    app.run_polling()
