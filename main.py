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

ADMINS = [7426624114] # ✅ Sirf aapki ID Admin hai

# --- CHANNELS SEQUENCE ---
CH1_ID, CH1_LINK = -1003641267601, "https://t.me/+mr5SZGOlW0U4YmQ1"
CH2_ID, CH2_LINK = -1003631779895, "https://t.me/+F9FiOh8EoHIxNjhl"
CH3_ID, CH3_LINK = -1003574535419, "https://t.me/+PanUv9-TO8cyNzhl"

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
            if member.status in ["kicked", "left"]: return False
        except UserNotParticipant: return False
        except: return False 
    return True

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1:
        if user_id not in ADMINS:
            if not await check_fsub(client, message):
                # ✅ Custom Button Names Updated here
                btns = [
                    [InlineKeyboardButton("📢 Tempest Main Channel", url=LINKS[0])],
                    [InlineKeyboardButton("📜 Tempest Anime List", url=LINKS[1])],
                    [InlineKeyboardButton("💬 Tempest Anime Chat Group", url=LINKS[2])],
                    [InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{(await client.get_me()).username}?start={message.command[1]}")]
                ]
                return await message.reply_text(
                    f"👋 **Hey {message.from_user.mention}!**\n\nFile download karne ke liye niche diye gaye **Channels** ko join karein aur phir niche button dabayein.", 
                    reply_markup=InlineKeyboardMarkup(btns)
                )
        
        try:
            msg_id = int(message.command[1])
            # Original buttons ke saath file copy hogi
            file_msg = await client.copy_message(chat_id=message.chat.id, from_chat_id=DB_CHANNEL_ID, message_id=msg_id)
            warn = await message.reply_text("⚠️ Ye file **10 minute** mein delete ho jayegi.")
            await asyncio.sleep(600) #
            await file_msg.delete()
            await warn.edit_text("🗑️ File auto-deleted.")
        except:
            await message.reply_text("❌ Error: Bot ko DB Channel mein Admin banayein.")
    else:
        # Welcome message with Main Channel Button
        await message.reply_photo(
            photo=START_PIC, 
            caption="👋 **Welcome to Tempest Anime Provider**", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Main Channel", url=LINKS[0])]])
        )

# --- MEDIA HANDLER (Fixed for Forwarded Posts with Buttons) ---
@bot.on_message(filters.private & (filters.document | filters.video | filters.audio) & filters.user(ADMINS))
async def save_media(client, message):
    # original message ko buttons ke saath DB mein copy karega
    sent_msg = await message.copy(DB_CHANNEL_ID)
    bot_username = (await client.get_me()).username
    link = f"https://t.me/{bot_username}?start={sent_msg.id}"
    await message.reply_text(f"✅ **Saved with Buttons!**\n\n🔗 Link: `{link}`", quote=True)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
