import os
import yt_dlp
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- वेब सर्वर सेटअप (Cronjob के पिंग के लिए) ---
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)
# ------------------------------------------------

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("नमस्ते! मुझे किसी भी Instagram Reel का लिंक भेजें और मैं उसे डाउनलोड करके दूंगा।")

async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "instagram.com" not in url:
        await update.message.reply_text("❌ कृपया सही Instagram लिंक भेजें।")
        return

    status_message = await update.message.reply_text("⏳ वीडियो डाउनलोड हो रहा है, कृपया प्रतीक्षा करें...")

    # --- यहाँ हमने आवाज़ के लिए नया फॉर्मेट सेट किया है ---
    ydl_opts = {
        'format': 'best[ext=mp4][vcodec!=none][acodec!=none]/best',
        'outtmpl': 'reel.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            caption = info_dict.get('description', '') or info_dict.get('title', '')
            
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
        
        with open('reel.mp4', 'rb') as video:
            await update.message.reply_video(video=video, caption=caption)
        
        os.remove('reel.mp4')
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text("❌ माफ़ करें, इंस्टाग्राम ने इस वीडियो को ब्लॉक कर दिया है या लिंक प्राइवेट है।")
        print(f"Error: {e}")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is not set!")
        return
        
    threading.Thread(target=run_web, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_reel))
    
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
