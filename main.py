import os
import asyncio
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, MessageIdInvalid
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_ID = 37197223
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
BOT_TOKEN = "8336671886:AAGrAv4g0CEc4X8kO1CFv7R8hucIMck60ac"
DB_CHANNEL_ID = -1003336472608 

ADMINS = [7426624114] 

# --- EXACT FSUB SETTINGS (As per your request) ---
CH1_ID = -1003631779895
CH1_LINK = "https://t.me/+F9FiOh8EoHIxNjhl"

CH2_ID = -1003641267601
CH2_LINK = "https://t.me/+mr5SZGOlW0U4YmQ1"

CH3_ID = -1003574535419
CH3_LINK = "https://t.me/+PanUv9-TO8cyNzhl"

FSUB_CHANNELS = [CH1_ID, CH2_ID, CH3_ID]
LINKS = [CH1_LINK, CH2_LINK, CH3_LINK]

START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg"

app = Flask(__name__)
@app.route('/')
def home(): return "Verification System: Active"
def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- BASE64 ENCODING UTILS ---
def encode(text):
    return base64.urlsafe_b64encode(str(text).encode('ascii')).decode('ascii').strip("=")

def decode(base64_string):
    padding = '=' * (4 - len(base64_string) % 4)
    return base64.urlsafe_b64decode((base64_string + padding).encode('ascii')).decode('ascii')

# --- FSUB VERIFICATION ---
async def check_fsub(client, user_id):
    for ch_id in FSUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status in ["kicked", "left"]:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            return False 
    return True

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1:
        data = message.command[1]
        try:
            msg_id = int(decode(data))
        except:
            return await message.reply_text("❌ Error: Invalid Link.")

        # Force Subscribe Check
        if user_id not in ADMINS:
            if not await check_fsub(client, user_id):
                btns = [
                    [InlineKeyboardButton("Join Channel 1", url=CH1_LINK)],
                    [InlineKeyboardButton("Join Channel 2", url=CH2_LINK)],
                    [InlineKeyboardButton("Join Channel 3", url=CH3_LINK)],
                    [InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{(await client.get_me()).username}?start={data}")]
                ]
                return await message.reply_text(
                    "👋 **Join all channels to get your file!**",
                    reply_markup=InlineKeyboardMarkup(btns)
                )
        
        try:
            # Explicitly getting original buttons from DB
            db_msg = await client.get_messages(DB_CHANNEL_ID, msg_id)
            file_msg = await client.copy_message(
                chat_id=message.chat.id, 
                from_chat_id=DB_CHANNEL_ID, 
                message_id=msg_id,
                reply_markup=db_msg.reply_markup
            )
            
            warn = await message.reply_text("⚠️ Auto-Deleting in 10 minutes.")
            await asyncio.sleep(600)
            await file_msg.delete()
            await warn.delete()
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")
    else:
        await message.reply_photo(photo=START_PIC, caption="**Welcome to Tempest**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=CH1_LINK)]]))

@bot.on_message(filters.private & filters.user(ADMINS))
async def save_media(client, message):
    try:
        # Saving with buttons and generating encoded link
        sent_msg = await message.copy(chat_id=DB_CHANNEL_ID, reply_markup=message.reply_markup)
        encoded_id = encode(sent_msg.id)
        link = f"https://t.me/{(await client.get_me()).username}?start={encoded_id}"
        await message.reply_text(f"✅ **Saved & Encoded!**\n\n🔗 **Link:** `{link}`", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ **Save Failed:** `{e}`")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()

