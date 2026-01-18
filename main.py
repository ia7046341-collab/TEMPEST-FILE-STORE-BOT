import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", "37197223"))
API_HASH = os.environ.get("API_HASH", "3a43ae287a696ee9a6a82fb79f605b75")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8336671886:AAGrAv4g0CEc4X8kO1CFv7R8hucIMck60ac")
DB_CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003641267601")) # Aapki nayi ID
FORCE_SUB = os.environ.get("FORCE_SUB_CHANNEL", "-1003691111238")
AUTO_DELETE = int(os.environ.get("AUTO_DELETE_TIME", "600"))

app = Flask(__name__)
@app.route('/')
def home(): return "Tempest Network is Active"

def run(): app.run(host="0.0.0.0", port=8080)

bot = Client("TempestBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- FORCE SUBSCRIBE CHECK ---
async def is_subscribed(client, message):
    if not FORCE_SUB: return True
    try:
        await client.get_chat_member(FORCE_SUB, message.from_user.id)
        return True
    except UserNotParticipant:
        invite_link = "https://t.me/ia704634" # Apne channel ka link yahan dalein
        await message.reply_text(
            "🛑 **Access Denied!**\n\nIs bot ko use karne ke liye aapko hamare updates channel ko join karna hoga.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join Channel", url=invite_link)]])
        )
        return False
    except Exception: return True

# --- START COMMAND (Customized) ---
@bot.on_message(filters.command("start"))
async def start(client, message):
    if not await is_subscribed(client, message): return
    
    if len(message.command) > 1:
        msg_id = int(message.command[1])
        try:
            sent_msg = await client.copy_message(chat_id=message.chat.id, from_chat_id=DB_CHANNEL_ID, message_id=msg_id)
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🗑️ Delete Now", callback_data="del")]])
            notification = await message.reply_text(f"🚀 **File Ready!**\n\nYe file {AUTO_DELETE//60} minute mein delete ho jayegi.", reply_markup=btn)
            
            await asyncio.sleep(AUTO_DELETE)
            await sent_msg.delete()
            await notification.edit_text("⌛ **File deleted automatically.**")
        except Exception as e:
            await message.reply_text("❌ File not found or deleted from database.")
    else:
        # Aapka customized welcome message
        welcome_text = (
            "👋 **Namaste! Welcome to Tempest Network**\n\n"
            "Main ek advanced File Store bot hoon. Mujhe koi bhi file (Video/Document) bhejein, "
            "main uska ek permanent shareable link bana dunga."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Updates", url="https://t.me/ia704634"),
             InlineKeyboardButton("🛠️ Support", url="https://t.me/ia704634")]
        ])
        await message.reply_text(welcome_text, reply_markup=buttons)

# --- FILE STORE LOGIC ---
@bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def store_file(client, message):
    if not await is_subscribed(client, message): return
    
    waiting_msg = await message.reply_text("⌛ **Processing... Please wait.**")
    sent_msg = await message.forward(DB_CHANNEL_ID)
    bot_username = (await client.get_me()).username
    share_link = f"https://t.me/{bot_username}?start={sent_msg.id}"
    
    await waiting_msg.edit_text(
        f"✅ **File Stored Successfully!**\n\n**Link:** `{share_link}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share Link", url=f"https://t.me/share/url?url={share_link}")]])
    )

if __name__ == "__main__":
    Thread(target=run).start()
    bot.run()
