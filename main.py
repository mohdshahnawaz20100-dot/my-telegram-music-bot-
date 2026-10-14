import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ["BOT_TOKEN"]
AUDIO_FILE = Path(__file__).parent / "sample.mp3"


# Render ke liye dummy web server (port scan timeout fix)
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), BaseHTTPRequestHandler)
    server.serve_forever()


async def start(update: Update, context):
    await update.message.reply_text(
        "🎵 Welcome to Music Bot!\nUse /audio to get the song."
    )


async def audio(update: Update, context):
    if not AUDIO_FILE.exists():
        await update.message.reply_text("Audio file nahi mili!")
        return
    with AUDIO_FILE.open("rb") as f:
        await update.message.reply_audio(audio=f)


def main():
    # Dummy server background me chalao
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio))
    app.run_polling()


if __name__ == "__main__":
    main()
