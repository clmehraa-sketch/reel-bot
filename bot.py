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

TOKEN = os.getenv("BOT_TOKEN")

L = instaloader.Instaloader()

# START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\n"
        "📥 Instagram Reel link bhejo.\n"
        "🤖 Main reel + caption bhej dunga."
    )

# REEL DOWNLOAD
async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    try:
        shortcode = url.split("/")[-2]

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Caption Text
        caption = post.caption if post.caption else "No caption found."

        # Download Reel
        L.download_post(post, target="downloads")

        for file in os.listdir("downloads"):
            if file.endswith(".mp4"):

                video_path = f"downloads/{file}"

                # SEND VIDEO
                await update.message.reply_video(
                    video=open(video_path, "rb"),
                    caption=caption[:1000]  # Telegram caption limit
                )

                break

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# APP
app = ApplicationBuilder().token(TOKEN).build()

# COMMANDS
app.add_handler(CommandHandler("start", start))

# MESSAGE HANDLER
app.add_handler(MessageHandler(filters.TEXT, download_reel))

print("✅ Bot Running...")

app.run_polling()
