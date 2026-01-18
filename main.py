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

ADMINS = [5029489287, 5893066075, 7426624114] 

# --- CHANNELS SEQUENCE ---
CH1_ID = -1003640815072
CH1_LINK = "https://t.me/+zIPvYrqHaZUMYTdl"

CH2_ID = -1003631779895
CH2_LINK = "https://t.me/+F9FiOh8EoHIxNjhl"

CH3_ID = -1003574535419
CH3_LINK = "https://t.me/+PanUv9-TO8cyNzhl"

FSUB_CHANNELS = [CH1_ID, CH2_ID, CH3_ID]
LINKS = [CH1_LINK, CH2_LINK, CH3_LINK]

START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Online"

def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def check_fsub(client, message):
    user_id = message.from_user.id
    for ch in FSUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch, user_id)
            if member.status in ["kicked", "left"]:
                return False
        except UserNotParticipant:
            return False
        except Exception as e:
            print(f"DEBUG Error: {ch} - {e}")
            return False 
    return True

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    
    if len(message.command) > 1:
        if user_id not in ADMINS:
            is_joined = await check_fsub(client, message)
            if not is_joined:
                buttons = [
                    [InlineKeyboardButton("Join Channel 1", url=LINKS[0]), InlineKeyboardButton("Join Channel 2", url=LINKS[1])],
                    [InlineKeyboardButton("Join Channel 3", url=LINKS[2])],
                    [InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{(await client.get_me()).username}?start={message.command[1]}")]
                ]
                return await message.reply_text(
                    f"Hey {message.from_user.mention}!\n\n**Channels join karne ke baad hi file milegi!**",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

        try:
            msg_id = int(message.command[1])
            await client.copy_message(message.chat.id, DB_CHANNEL_ID, msg_id)
        except:
            await message.reply_text("❌ Error: Bot ko DB Channel mein Admin banayein.")
            
    else:
        welcome_text = "👋 **Welcome to Tempest Anime Provider**"
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Updates", url=LINKS[0])]])
        await message.reply_photo(photo=START_PIC, caption=welcome_text, reply_markup=btns)

# --- MEDIA HANDLER (Save Feature with Fixed Line 94) ---
@bot.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def save_media(client, message):
    if message.from_user.id not in ADMINS:
        return

    sent_msg = await message.forward(DB_CHANNEL_ID)
    bot_username = (await client.get_me()).username
    file_link = f"https://t.me/{bot_username}?start={sent_msg.id}"
    
    # Corrected syntax here
    await message.reply_text(
        f"✅ **File Saved!**\n\n🔗 **Link:** `{file_link}`",
        quote=True
    )

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()

