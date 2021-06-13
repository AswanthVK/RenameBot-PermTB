import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import time
import os
import sqlite3
import asyncio

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

import pyrogram

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.errors import UserNotParticipant

from plugins.rename_file import rename_doc


@Client.on_message(filters.command(["help"]))
def help_user(bot, update):
    bot.send_message(
        chat_id=update.chat.id,
        text=script.HELP_USER,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="⭕️ Contact DEV ⭕️", url="https://t.me/prgofficial")]]),
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@Client.on_message(filters.command(["start"]))
def send_start(bot, update):
    # logger.info(update)
    
    bot.send_message(
        chat_id=update.chat.id,
        text=script.START_TEXT.format(update.from_user.first_name),
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )


@Client.on_message(filters.command(["upgrade"]))
def upgrade(bot, update):
    # logger.info(update)

    bot.send_message(
        chat_id=update.chat.id,
        text=script.UPGRADE_TEXT,
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )

    
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.voice | filters.video_note))
async def rename_cb(bot, update):
 
    file = update.document or update.video or update.audio or update.voice or update.video_note
    try:
        filename = file.file_name
    except:
        filename = "Not Available"

    if Config.UPDATE_CHANNEL:
        try:
            user = await bot.get_chat_member(Config.UPDATE_CHANNEL, update.from_user.id)
            if user.status == "kicked":
              await bot.edit_message_text(text=Translation.BANNED_USER_TEXT, message_id=fmsg.message_id)
              return
        except UserNotParticipant:
            await bot.edit_message_text(chat_id=update.chat.id, text=Translation.FORCE_SUBSCRIBE_TEXT, message_id=fmsg.message_id, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Join Updates Channel", url=f"https://telegram.me/{Config.UPDATE_CHANNEL}")]]))
            return
        except Exception:
            await bot.edit_message_text(chat_id=update.chat.id, text=Translation.SOMETHING_WRONG, message_id=fmsg.message_id)
            return

    if update.from_user.id not in Config.AUTH_USERS:
        # restrict free users from sending more links
        if str(update.from_user.id) in Config.ADL_BOT_RQ:
            current_time = time.time()
            previous_time = Config.ADL_BOT_RQ[str(update.from_user.id)]
            process_max_timeout = round(Config.PROCESS_MAX_TIMEOUT/60)
            present_time = round(Config.PROCESS_MAX_TIMEOUT-(current_time - previous_time))
            Config.ADL_BOT_RQ[str(update.from_user.id)] = time.time()
            if round(current_time - previous_time) < Config.PROCESS_MAX_TIMEOUT:
                await bot.edit_message_text(chat_id=update.chat.id, text=Translation.FREE_USER_LIMIT_Q_SZE.format(process_max_timeout, present_time), disable_web_page_preview=True, parse_mode="html", message_id=fmsg.message_id)
                return
        else:
            Config.ADL_BOT_RQ[str(update.from_user.id)] = time.time()
   
    await bot.send_message(
        chat_id=update.chat.id,
        text="<b>File Name</b> : <code>{}</code> \n\nSelect the desired option below 😇".format(filename),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="📝 RENAME 📝", callback_data="rename_button")],
                                                [InlineKeyboardButton(text="✖️ CANCEL ✖️", callback_data="cancel_e")]]),
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True   
    )   


async def cancel_extract(bot, update):
    
    await bot.send_message(
        chat_id=update.chat.id,
        text="Process Cancelled 🙃",
    )
