import os, asyncio, base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_ID = 37197223
API_HASH = "3a43ae287a696ee9a6a82fb79f605b75"
# Naya token yahan replace kar diya hai
BOT_TOKEN = "8336671886:AAGrAv4g0CEc4X8kO1CFv7R8hucIMck60ac" 
DB_CHANNEL_ID = -1003336472608 
ADMINS = [7426624114] 

# --- UPDATED FSUB CHANNELS ---
CH1_ID = -1003641267601
CH1_LINK = "https://t.me/+mr5SZGOlW0U4YmQ1"
CH2_ID = -1003625900383
CH2_LINK = "https://t.me/+BsibgbLhN48xNDdl"

FSUB_CHANNELS = [CH1_ID, CH2_ID]
LINKS = [CH1_LINK, CH2_LINK]

START_PIC = "https://graph.org/file/528ff7a62d3c63dc4d030-21c629267007f575ec.jpg"

app = Flask(__name__)
@app.route('/')
def home(): return "Tempest Bot: Active"
def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- UTILS ---
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
        except UserNotParticipant: return False
        except: continue 
    return True

async def auto_del(m):
    await asyncio.sleep(600)
    try: await m.delete()
    except: pass

# --- BATCH COMMAND ---
@bot.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch(client, message):
    if len(message.command) < 3:
        return await message.reply_text("❌ Usage: `/batch [Start_ID] [End_ID]`")
    s, e = message.command[1], message.command[2]
    me = await client.get_me()
    link = f"https://t.me/{me.username}?start={encode(f'BATCH-{s}-{e}')}"
    await message.reply_text(f"✅ **Batch Link Ready:**\n`{link}`")

# --- START COMMAND ---
@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    user_id = message.from_user.id
    me = await client.get_me()
    
    if len(message.command) > 1:
        data = message.command[1]
        
        if user_id not in ADMINS and not await check_fsub(client, user_id):
            btns = [[InlineKeyboardButton(f"Join Channel {i+1}", url=LINKS[i])] for i in range(len(LINKS))]
            btns.append([InlineKeyboardButton("♻️ Try Again", url=f"https://t.me/{me.username}?start={data}")])
            return await message.reply_text("👋 **Join all channels to get your file!**", reply_markup=InlineKeyboardMarkup(btns))

        try:
            decoded_val = decode(data)
            ids_to_send = []

            if decoded_val.startswith("BATCH-"):
                _, s_id, e_id = decoded_val.split("-")
                ids_to_send = list(range(int(s_id), int(e_id) + 1))
                await message.reply_text("🚀 **Sending your Batch Files...**")
            else:
                ids_to_send = [int(decoded_val)]

            for msg_id in ids_to_send:
                try:
                    db_msg = await client.get_messages(DB_CHANNEL_ID, msg_id)
                    file_msg = await client.copy_message(message.chat.id, DB_CHANNEL_ID, msg_id, reply_markup=db_msg.reply_markup)
                    asyncio.create_task(auto_del(file_msg))
                    if len(ids_to_send) > 1: await asyncio.sleep(0.7)
                except: continue

            await message.reply_text("⚠️ **Files will be auto-deleted in 10 minutes.**")
        except Exception as e:
            await message.reply_text(f"❌ Error: `{e}`")
    else:
        await message.reply_photo(photo=START_PIC, caption="**Welcome to Tempest**", 
                                  reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=CH1_LINK)]]))

# --- ADMIN SAVE ONLY (Auto-Post Removed) ---
@bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(["start", "batch"]))
async def save_only(client, message):
    try:
        sent_msg = await message.copy(chat_id=DB_CHANNEL_ID)
        me = await client.get_me()
        link = f"https://t.me/{me.username}?start={encode(sent_msg.id)}"
        
        await message.reply_text(f"✅ **Saved to Database!**\n\nID: `{sent_msg.id}`\n🔗 **Link:** `{link}`", quote=True)
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
