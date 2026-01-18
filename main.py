import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_ID = 37197223
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
BOT_TOKEN = "8336671886:AAGrAv4g0CEc4X8kO1CFv7R8hucIMck60ac"
DB_CHANNEL_ID = -1003641267601 
FORCE_SUB = -1003691111238
AUTO_DELETE = 600

# Aapka naya photo aur links
START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg" 
UPDATE_LINK = "https://t.me/+mr5SZGOlW0U4YmQ1"
SUPPORT_LINK = "https://t.me/+zIPvYrqHaZU4YTdl"

app = Flask(__name__)
@app.route('/')
def home(): return "Tempest is Live"

def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("start"))
async def start(client, message):
    try:
        await client.get_chat_member(FORCE_SUB, message.from_user.id)
    except UserNotParticipant:
        btn = [[InlineKeyboardButton("📢 Join Updates", url=UPDATE_LINK)]]
        return await message.reply_text("🛑 **Access Denied!**\n\nKripya pehle hamare channel ko join karein.", reply_markup=InlineKeyboardMarkup(btn))
    except: pass

    if len(message.command) > 1:
        data = message.command[1]
        try:
            # Fix for ValueError: invalid literal for int()
            msg_id = int(data) 
            sent_msg = await client.copy_message(message.chat.id, DB_CHANNEL_ID, msg_id)
            await asyncio.sleep(AUTO_DELETE)
            await sent_msg.delete()
        except:
            await message.reply_text("❌ Invalid link ya file delete ho gayi hai.")
    else:
        welcome_text = "👋 **Welcome to Tempest Anime Provider**\n\nMain aapki anime files ko store karke links bana sakta hoon. Mujhe koi bhi file bhejein!"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Update", url=UPDATE_LINK),
             InlineKeyboardButton("🛠️ Support", url=SUPPORT_LINK)]
        ])
        try:
            await message.reply_photo(photo=START_PIC, caption=welcome_text, reply_markup=buttons)
        except:
            await message.reply_text(text=welcome_text, reply_markup=buttons)

@bot.on_message(filters.private & (filters.document | filters.video | filters.photo))
async def store_file(client, message):
    try:
        msg = await message.forward(DB_CHANNEL_ID)
        bot_username = (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={msg.id}"
        await message.reply_text(f"✅ **File Stored!**\n\nLink: `{link}`")
    except:
        await message.reply_text("❌ Error: Bot ko DB Channel mein Admin banayein!")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
