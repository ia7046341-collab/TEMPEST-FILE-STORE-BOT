import os
import asyncio
import base64
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

ADMINS = [7426624114] 

# --- FSUB SETTINGS ---
CH1_ID = -1003631779895
CH1_LINK = "https://t.me/+F9FiOh8EoHIxNjhl"
CH2_ID = -1003641267601
CH2_LINK = "https://t.me/+mr5SZGOlW0U4YmQ1"
CH3_ID = -1003574535419
CH3_LINK = "https://t.me/+PanUv9-TO8cyNzhl"

FSUB_CHANNELS = [CH1_ID, CH2_ID, CH3_ID]
LINKS = [CH1_LINK, CH2_LINK, CH3_LINK]

START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg"

# --- WEB SERVER FOR ALIVE ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running"
def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- UTILS (Base64) ---
def encode(text):
    return base64.urlsafe_b64encode(str(text).encode('ascii')).decode('ascii').strip("=")

def decode(base64_string):
    padding = '=' * (4 - len(base64_string) % 4)
    return base64.urlsafe_b64decode((base64_string + padding).encode('ascii')).decode('ascii')

async def check_fsub(client, user_id):
    for ch_id in FSUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status in ["kicked", "left"]: return False
        except Exception: return False 
    return True

# --- COMMANDS ---

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    if len(message.command) > 1:
        data = message.command[1]
        try:
            decoded_text = decode(data)
            # Batch logic check
            if decoded_text.startswith("BATCH-"):
                _, s_id, e_id = decoded_text.split("-")
                msg_ids = range(int(s_id), int(e_id) + 1)
            else:
                msg_ids = [int(decoded_text)]
        except:
            return await message.reply_text("❌ Error: Invalid Link.")

        # Force Subscribe
        if user_id not in ADMINS and not await check_fsub(client, user_id):
            btns = [[InlineKeyboardButton(f"Join Channel {i+1}", url=LINKS[i])] for i in range(len(LINKS))]
            btns.append([InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{(await client.get_me()).username}?start={data}")])
            return await message.reply_text("👋 **Please join our channels to access the file!**", reply_markup=InlineKeyboardMarkup(btns))
        
        # Sending Files
        msg = await message.reply_text("⏳ **Processing...**")
        sent_msgs = []
        try:
            for m_id in msg_ids:
                db_msg = await client.get_messages(DB_CHANNEL_ID, m_id)
                copy = await client.copy_message(message.chat.id, DB_CHANNEL_ID, m_id, reply_markup=db_msg.reply_markup)
                sent_msgs.append(copy)
                await asyncio.sleep(0.5)
            
            await msg.edit("⚠️ **Files will be deleted in 10 minutes to avoid copyright.**")
            await asyncio.sleep(600)
            for s in sent_msgs: await s.delete()
            await msg.delete()
        except Exception as e:
            await msg.edit(f"❌ **Error:** `{e}`")
    else:
        await message.reply_photo(photo=START_PIC, caption="**Welcome to Tempest Bot**\n\nSend me any file to get a shareable link.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Support", url=CH1_LINK)]]))

@bot.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch(client, message):
    if len(message.command) < 3:
        return await message.reply_text("❌ **Usage:** `/batch [Start_ID] [End_ID]`")
    
    s, e = message.command[1], message.command[2]
    encoded_string = encode(f"BATCH-{s}-{e}")
    link = f"https://t.me/{(await client.get_me()).username}?start={encoded_string}"
    
    await message.reply_text(f"✅ **Batch Link Ready:**\n\n🔗 `{link}`\n\n📂 Range: `{s}` to `{e}`")

@bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(["start", "batch"]))
async def save_media(client, message):
    try:
        # DB Mein Save karna
        sent_msg = await message.copy(chat_id=DB_CHANNEL_ID)
        link = f"https://t.me/{(await client.get_me()).username}?start={encode(sent_msg.id)}"
        
        # Sirf ID aur Link dikhayega (No Auto-Post)
        await message.reply_text(
            f"✅ **File Saved!**\n\n"
            f"🆔 **Message ID:** `{sent_msg.id}`\n"
            f"🔗 **Link:** `{link}`",
            quote=True
        )
    except Exception as e:
        await message.reply_text(f"❌ **Failed:** `{e}`")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
