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
    # Render अपने आप PORT देता है
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host="0.0.0.0", port=port)
# ------------------------------------------------

# Render के Environment Variables से आपका टोकन लेगा
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("नमस्ते! मुझे किसी भी Instagram Reel का लिंक भेजें और मैं उसे डाउनलोड करके दूंगा।")

async def download_reel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    # चेक करें कि लिंक इंस्टाग्राम का ही है या नहीं
    if "instagram.com" not in url:
        await update.message.reply_text("❌ कृपया सही Instagram लिंक भेजें।")
        return

    status_message = await update.message.reply_text("⏳ वीडियो और कैप्शन निकाला जा रहा है, कृपया प्रतीक्षा करें...")

    # yt-dlp की सेटिंग्स
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'reel.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # वीडियो डाउनलोड करें और जानकारी निकालें
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            caption = info_dict.get('description', '') or info_dict.get('title', '')
            
            if len(caption) > 1024:
                caption = caption[:1020] + "..."
        
        # टेलीग्राम पर वीडियो भेजें
        with open('reel.mp4', 'rb') as video:
            await update.message.reply_video(video=video, caption=caption)
        
        # सर्वर से फाइल डिलीट करें
        os.remove('reel.mp4')
        await status_message.delete()
        
    except Exception as e:
        await status_message.edit_text("❌ माफ़ करें, इंस्टाग्राम ने इस वीडियो को ब्लॉक कर दिया है या लिंक प्राइवेट है।")
        print(f"Error: {e}")

def main():
    if not TOKEN:
        print("Error: BOT_TOKEN environment variable is not set!")
        return
        
    # बॉट शुरू होने से पहले डमी वेबसाइट को बैकग्राउंड में चालू करें
    threading.Thread(target=run_web, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_reel))
    
    # पुरानी रुकी हुई रिक्वेस्ट क्रैश नहीं करेंगी
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
    
