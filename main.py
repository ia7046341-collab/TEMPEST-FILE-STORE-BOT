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
DB_CHANNEL_ID = -1003336472608 

# ADMINS - Inhe membership check nahi dikhega
ADMINS = [5029489287, 5893066075, 7426624114] 

# --- 4 CHANNELS ---
FSUB_CHANNELS = [-1003691111238, -1001234567890, -1003574535419, -1003631779895] 
LINKS = [
    "https://t.me/+mr5SZGOlW0U4YmQ1", 
    "https://t.me/+zIPvYrqHaZU4YTdl",
    "https://t.me/+F9FiOh8EoHIxNjhl",
    "https://t.me/+PanUv9-TO8cyNzhl"
]

START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Membership Check Function
async def check_fsub(client, message):
    for ch in FSUB_CHANNELS:
        try:
            await client.get_chat_member(ch, message.from_user.id)
        except UserNotParticipant:
            return False
        except Exception:
            return False 
    return True

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    
    # CASE 1: File Link se aane par
    if len(message.command) > 1:
        if user_id not in ADMINS:
            is_joined = await check_fsub(client, message)
            if not is_joined:
                # 4 Buttons + Try Again
                buttons = [
                    [InlineKeyboardButton("Join Channel 1", url=LINKS[0]), InlineKeyboardButton("Join Channel 2", url=LINKS[1])],
                    [InlineKeyboardButton("Join Channel 3", url=LINKS[2]), InlineKeyboardButton("Join Channel 4", url=LINKS[3])],
                    [InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{(await client.get_me()).username}?start={message.command[1]}")]
                ]
                return await message.reply_text(
                    f"Hey {message.from_user.mention}!\n\n**Channal join karne ke baad aapko aapki files mil jayegi!**",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

        # File Delivery
        try:
            msg_id = int(message.command[1])
            sent_msg = await client.copy_message(message.chat.id, DB_CHANNEL_ID, msg_id)
            del_msg = await message.reply_text("✅ **File Sent!** Deleting in 30 mins.")
            await asyncio.sleep(1800)
            await sent_msg.delete()
            await del_msg.edit("🛑 **File Deleted!**")
        except:
            await message.reply_text("❌ Link invalid or file deleted from database.")
            
    # CASE 2: Normal Welcome Message
    else:
        welcome_text = "👋 **Welcome to Tempest Anime Provider**\n\nChannal join karne ke baad aapko aapki files mil jayegi."
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Updates", url=LINKS[0])]])
        await message.reply_photo(photo=START_PIC, caption=welcome_text, reply_markup=btns)

# Admin Only: Store files
@bot.on_message(filters.private & (filters.document | filters.video | filters.photo))
async def store_file(client, message):
    if message.from_user.id not in ADMINS:
        return 
    try:
        msg = await message.forward(DB_CHANNEL_ID)
        link = f"https://t.me/{(await client.get_me()).username}?start={msg.id}"
        await message.reply_text(f"✅ **Link Generated:**\n\n`{link}`")
    except:
        await message.reply_text("❌ Error: Make sure Bot is Admin in DB Channel!")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
