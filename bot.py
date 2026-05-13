from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import instaloader
import os

TOKEN = os.getenv("BOT_TOKEN")

L = instaloader.Instaloader()

async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    try:
        shortcode = url.split("/")[-2]

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        L.download_post(post, target="downloads")

        for file in os.listdir("downloads"):
            if file.endswith(".mp4"):
                video_path = f"downloads/{file}"

                await update.message.reply_video(video=open(video_path, "rb"))

                break

    except Exception as e:
        await update.message.reply_text(str(e))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, download_reel))

print("Bot Running...")

app.run_polling()
