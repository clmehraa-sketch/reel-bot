from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import instaloader
import os

from flask import Flask
from threading import Thread

# =========================
# KEEP ALIVE WEB SERVER
# =========================

web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running!"

def run():
    web_app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========================
# TELEGRAM BOT TOKEN
# =========================

TOKEN = os.getenv("BOT_TOKEN")

# =========================
# INSTAGRAM LOGIN SESSION
# =========================

L = instaloader.Instaloader()

# YOUR INSTAGRAM USERNAME
USERNAME = "your_instagram_username"

# LOAD SESSION FILE
L.load_session_from_file(USERNAME)

# =========================
# START COMMAND
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📥 Instagram Reel link bhejo.\n"
        "🤖 Main reel + caption download karke bhej dunga."
    )

# =========================
# DOWNLOAD REEL
# =========================

async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    try:

        # SHORTCODE
        shortcode = url.split("/")[-2]

        # GET POST
        post = instaloader.Post.from_shortcode(
            L.context,
            shortcode
        )

        # CAPTION
        caption = post.caption if post.caption else "No caption found."

        # DOWNLOAD
        L.download_post(post, target="downloads")

        # SEND VIDEO
        for file in os.listdir("downloads"):

            if file.endswith(".mp4"):

                video_path = f"downloads/{file}"

                await update.message.reply_video(
                    video=open(video_path, "rb"),
                    caption=caption[:1000]
                )

                # DELETE FILE AFTER SEND
                os.remove(video_path)

                break

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error: {e}"
        )

# =========================
# TELEGRAM APP
# =========================

app = ApplicationBuilder().token(TOKEN).build()

# START COMMAND
app.add_handler(
    CommandHandler("start", start)
)

# MESSAGE HANDLER
app.add_handler(
    MessageHandler(filters.TEXT, download_reel)
)

# =========================
# KEEP ALIVE
# =========================

keep_alive()

print("✅ Bot Running...")

# =========================
# RUN BOT
# =========================

app.run_polling()
