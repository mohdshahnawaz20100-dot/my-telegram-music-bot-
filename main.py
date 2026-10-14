
import os
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
AUDIO_FILE = Path(__file__).parent / "sample.mp3"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Welcome to Music Bot!\nUse /audio to receive music."
    )

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AUDIO_FILE.exists():
        await update.message.reply_text("Audio file abhi upload nahi hui.")
        return

    with AUDIO_FILE.open("rb") as f:
        await update.message.reply_audio(audio=f, title="Sample Music")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio))
    app.run_polling()

if __name__ == "__main__":
    main()
      
