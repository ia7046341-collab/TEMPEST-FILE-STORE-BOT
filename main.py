import os
from threading import Thread
from flask import Flask
from pyrogram import Client, filters

# ---------------- CONFIGURATION ---------------- #
API_ID = 37197223
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
BOT_TOKEN = "8336671886:AAGrAv4g0CEc4X8kO1CFv7R8hucIMck60ac"

# ---------------- FLASK KEEP-ALIVE ---------------- #
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------- BOT CLIENT ---------------- #
bot = Client(
    "tempest_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Hello! Tempest Bot is alive and running on Render Free Tier.")

# ---------------- MAIN EXECUTION ---------------- #
if __name__ == "__main__":
    keep_alive()  # Starts the web server
    bot.run()     # Starts the Telegram bot
