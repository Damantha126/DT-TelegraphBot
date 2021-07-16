import os
import logging
import time
import math
import json
import string
import random
import traceback
import asyncio
import datetime
import aiofiles
from random import choice
from pyrogram import Client, filters
from config import Config
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import Database




DTbot = Client(
   "Telegraph Uploader",
   api_id=Config.APP_ID,
   api_hash=Config.API_HASH,
   bot_token=Config.TG_BOT_TOKEN,
)

## --- Sub Configs --- ##
BOT_USERNAME = Config.BOT_USERNAME
TG_BOT_TOKEN = Config.TG_BOT_TOKEN
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH
DB_CHANNEL = Config.DB_CHANNEL
BOT_OWNER = Config.BOT_OWNER
db = Database(Config.DATABASE_URL, BOT_USERNAME)
broadcast_ids = {}
Bot = Client(BOT_USERNAME, bot_token=TG_BOT_TOKEN, api_id=APP_ID, api_hash=API_HASH)

@DTbot.on_message(filters.command("start"))
async def start(client, message):
   if message.chat.type == 'private':
       await DTbot.send_message(
               chat_id=message.chat.id,
               text="""<b>Hey There, I'm Telegraph Bot
I can upload photos or videos to telegraph. Made by @Damantha_Jasinghe 🇱🇰
Hit help button to find out more about how to use me</b>""",   
                            reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Help", callback_data="help"),
                                        InlineKeyboardButton(
                                            "Suppor Group", url="https://t.me/AnkiSupport_Official")
                                    ],[
                                      InlineKeyboardButton(
                                            "Updates", url="https://t.me/ankivectorUpdates")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")

@DTbot.on_message(filters.command("help"))
async def help(client, message):
    if message.chat.type == 'private':   
        await DTbot.send_message(
               chat_id=message.chat.id,
               text="""<b>Telegraph Bot Help!
Just send a photo or video less than 5mb file size, I'll upload it to telegraph.
~ @ankivectorUpdates</b>""",
        reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Back", callback_data="start"),
                                        InlineKeyboardButton(
                                            "About", callback_data="about"),
                                  ],[
                                        InlineKeyboardButton(
                                            "Updates", url="https://t.me/ankivectorUpdates")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")

@DTbot.on_message(filters.command("about"))
async def about(client, message):
    if message.chat.type == 'private':   
        await DTbot.send_message(
               chat_id=message.chat.id,
               text="""<b>About Telegraph Bot!</b>
<b>♞ Developer:</b> <a href="https://t.me/Damantha_Jasinghe">Damantha 🇱🇰</a>
<b>♞ Support:</b> <a href="https://t.me/AnkiSupport_Official">Anki Vector Support</a>
<b>♞ Library:</b> <a href="https://github.com/pyrogram/pyrogram">Pyrogram</a>
<b>~ @ankivectorUpdates</b>""",
     reply_markup=InlineKeyboardMarkup(
                                [[
                                        InlineKeyboardButton(
                                            "Back", callback_data="help"),
                                        InlineKeyboardButton(
                                            "Support Group", url="https://t.me/AnkiSupport_Official")
                                    ]]
                            ),        
            disable_web_page_preview=True,        
            parse_mode="html")

@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(BOT_OWNER) & filters.reply)
async def broadcast_(c, m):
	all_users = await db.get_all_users()
	broadcast_msg = m.reply_to_message
	while True:
	    broadcast_id = ''.join([random.choice(string.ascii_letters) for i in range(3)])
	    if not broadcast_ids.get(broadcast_id):
	        break
	out = await m.reply_text(
	    text = f"Broadcast Started! You will be notified with log file when all the users are notified."
	)
	start_time = time.time()
	total_users = await db.total_users_count()
	done = 0
	failed = 0
	success = 0
	broadcast_ids[broadcast_id] = dict(
	    total = total_users,
	    current = done,
	    failed = failed,
	    success = success
	)
	async with aiofiles.open('broadcast.txt', 'w') as broadcast_log_file:
	    async for user in all_users:
	        sts, msg = await send_msg(
	            user_id = int(user['id']),
	            message = broadcast_msg
	        )
	        if msg is not None:
	            await broadcast_log_file.write(msg)
	        if sts == 200:
	            success += 1
	        else:
	            failed += 1
	        if sts == 400:
	            await db.delete_user(user['id'])
	        done += 1
	        if broadcast_ids.get(broadcast_id) is None:
	            break
	        else:
	            broadcast_ids[broadcast_id].update(
	                dict(
	                    current = done,
	                    failed = failed,
	                    success = success
	                )
	            )
	if broadcast_ids.get(broadcast_id):
	    broadcast_ids.pop(broadcast_id)
	completed_in = datetime.timedelta(seconds=int(time.time()-start_time))
	await asyncio.sleep(3)
	await out.delete()
	if failed == 0:
	    await m.reply_text(
	        text=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
	        quote=True
	    )
	else:
	    await m.reply_document(
	        document='broadcast.txt',
	        caption=f"broadcast completed in `{completed_in}`\n\nTotal users {total_users}.\nTotal done {done}, {success} success and {failed} failed.",
	        quote=True
	    )
	await os.remove('broadcast.txt')

@Bot.on_message(filters.private & filters.command("stats") & filters.user(BOT_OWNER))
async def sts(c, m):
	total_users = await db.total_users_count()
	await m.reply_text(text=f"**Total Users in DB:** `{total_users}`", parse_mode="Markdown", quote=True)

      
@DTbot.on_message(filters.photo)
async def telegraphphoto(client, message):
    msg = await message.reply_text("Uploading To Telegraph...")
    download_location = await client.download_media(
        message=message, file_name='root/jetg')
    try:
        response = upload_file(download_location)
    except:
        await msg.edit_text("Photo size should be less than 5mb!") 
    else:
        await msg.edit_text(f'**Uploaded To Telegraph!\n\n👉 https://telegra.ph{response[0]}\n\nJoin @ankivectorUpdates**',
            disable_web_page_preview=True,
        )
    finally:
        os.remove(download_location)

@DTbot.on_message(filters.video)
async def telegraphvid(client, message):
    msg = await message.reply_text("Uploading To Telegraph...")
    download_location = await client.download_media(
        message=message, file_name='root/jetg')
    try:
        response = upload_file(download_location)
    except:
        await msg.edit_text("Video size should be less than 5mb!") 
    else:
        await msg.edit_text(f'**Uploaded To Telegraph!\n\n👉 https://telegra.ph{response[0]}\n\nJoin @ankivectorUpdates**',
            disable_web_page_preview=True,
        )
    finally:
        os.remove(download_location)

@DTbot.on_message(filters.animation)
async def telegraphgif(client, message):
    msg = await message.reply_text("Uploading To Telegraph...")
    download_location = await client.download_media(
        message=message, file_name='root/jetg')
    try:
        response = upload_file(download_location)
    except:
        await msg.edit_text("Gif size should be less than 5mb!") 
    else:
        await msg.edit_text(f'**Uploaded To Telegraph!\n\n👉 https://telegra.ph{response[0]}\n\nJoin @ankivectorUpdates**',
            disable_web_page_preview=True,
        )
    finally:
        os.remove(download_location)

@DTbot.on_callback_query()
async def button(bot, update):
      cb_data = update.data
      if "help" in cb_data:
        await update.message.delete()
        await help(bot, update.message)
      elif "about" in cb_data:
        await update.message.delete()
        await about(bot, update.message)
      elif "start" in cb_data:
        await update.message.delete()
        await start(bot, update.message)
      elif "broadcast" in cb_data:
        await update.message.delete()
        await start(bot, update.message)
      elif "stats" in cb_data:
        await update.message.delete()
        await start(bot, update.message)
print(
    """
Bot Started!
Join @ankivectorUpdates 🆗
"""
)

DTbot.run()
