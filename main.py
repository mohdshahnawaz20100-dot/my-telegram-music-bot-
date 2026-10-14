import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ["BOT_TOKEN"]
AUDIO_FILE = Path(__file__).parent / "sample.mp3"


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
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio))
    app.run_polling()


if __name__ == "__main__":
    main()
import subprocess

async def song(update: Update, context):
    if not context.args:
        await update.message.reply_text("Song ka naam likh bhai!\nExample: /song Kesariya")
        return
    
    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 '{query}' dhundh raha hu...")
    
    try:
        # YouTube pe search karke pehla result ka link nikal
        result = subprocess.run(
            ["yt-dlp", f"ytsearch1:{query}", "--get-url", "--no-warnings"],
            capture_output=True, text=True, timeout=30
        )
        link = result.stdout.strip()
        
        if link:
            await update.message.reply_text(f"🎵 Ye le bhai:\n{link}")
        else:
            await update.message.reply_text("Kuch nahi mila, dusra naam try kar.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
import os
import re
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler

TOKEN = os.environ["BOT_TOKEN"]
AUDIO_FILE = Path(__file__).parent / "sample.mp3"
DOWNLOAD_DIR = Path("/tmp/music")
DOWNLOAD_DIR.mkdir(exist_ok=True)


def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), BaseHTTPRequestHandler)
    server.serve_forever()


async def start(update: Update, context):
    await update.message.reply_text(
        "🎵 Welcome to Music Bot!\n\n"
        "/audio - Sample song sun\n"
        "/song <naam> - Koi bhi gaana download kar\n\n"
        "Example: /song Kesariya"
    )


async def audio(update: Update, context):
    if not AUDIO_FILE.exists():
        await update.message.reply_text("Audio file nahi mili!")
        return
    with AUDIO_FILE.open("rb") as f:
        await update.message.reply_audio(audio=f)


def safe_filename(name):
    name = re.sub(r'[^\w\s-]', '', name).strip()
    return name[:50] if name else "song"


async def song(update: Update, context):
    if not context.args:
        await update.message.reply_text(
            "Song ka naam likh bhai!\nExample: /song Kesariya"
        )
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text(f"🔍 '{query}' dhundh raha hu...")

    try:
        # YouTube se best match ka URL nikal
        result = subprocess.run(
            ["yt-dlp", f"ytsearch1:{query}", "--get-url", "--no-warnings", "-f", "bestaudio"],
            capture_output=True, text=True, timeout=60
        )
        video_url = result.stdout.strip().split("\n")[0]

        if not video_url:
            await msg.edit_text("❌ Kuch nahi mila, dusra naam try kar.")
            return

        await msg.edit_text("⬇️ Download kar raha hu, thoda wait kar...")

        filename = safe_filename(query)
        output_path = DOWNLOAD_DIR / f"{filename}.mp3"

        # Audio download karo
        dl = subprocess.run(
            [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "--audio-quality", "128K",
                "-o", str(DOWNLOAD_DIR / f"{filename}.%(ext)s"),
                video_url,
                "--no-warnings"
            ],
            capture_output=True, text=True, timeout=180
        )

        if not output_path.exists():
            # fallback: koi bhi mp3 dhundh
            mp3s = list(DOWNLOAD_DIR.glob("*.mp3"))
            if mp3s:
                output_path = mp3s[0]
            else:
                await msg.edit_text("❌ Download fail ho gaya.")
                return

        # File size check (Telegram limit ~50MB)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        if size_mb > 49:
            await msg.edit_text(f"❌ File bahut badi hai ({size_mb:.1f}MB). Chhota gaana try kar.")
            output_path.unlink(missing_ok=True)
            return

        await msg.edit_text("📤 Bhej raha hu...")

        with output_path.open("rb") as f:
            await update.message.reply_audio(
                audio=f,
                title=query,
                performer="Music Bot"
            )

        # Cleanup
        output_path.unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        await msg.edit_text("❌ Timeout ho gaya, dobara try kar.")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:200]}")


def main():
    threading.Thread(target=run_dummy_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("audio", audio))
    app.add_handler(CommandHandler("song", song))
    app.run_polling()


if __name__ == "__main__":
    main()
