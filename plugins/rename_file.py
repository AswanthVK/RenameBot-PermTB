import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import os
import time
import random
import asyncio
import pyrogram

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import script

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait
from pyrogram.emoji import *

from plugins.helpers import progress_for_pyrogram, take_screen_shot

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from PIL import Image
from database.database import *


async def force_name(bot, message):

    await bot.send_message(
        message.reply_to_message.from_user.id,
        "Enter new name for media\n\nNote : Extension not required",
        reply_to_message_id=message.reply_to_message.message_id,
        reply_markup=ForceReply(True)
    )


@Client.on_message(filters.private & filters.reply & filters.text)
async def cus_name(bot, message):
    
    if (message.reply_to_message.reply_markup) and isinstance(message.reply_to_message.reply_markup, ForceReply):
        asyncio.create_task(rename_doc(bot, message))     
    else:
        print('No media present')

    
async def rename_doc(bot, message):
    
    mssg = await bot.get_messages(
        message.chat.id,
        message.reply_to_message.message_id
    )    
    
    media = mssg.reply_to_message
    
    if media.empty:
        await message.reply_text('Why did you delete that 😕', True)
        return
        
    filetype = media.document or media.video or media.audio or media.voice or media.video_note
    try:
        actualname = filetype.file_name
        splitit = actualname.split(".")
        extension = (splitit[-1])
    except:
        extension = "mkv"

    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=message.reply_to_message.message_id,
        revoke=True
    )

    if message.from_user.id not in Config.BANNED_USERS:
        file_name = message.text
        description = script.CUSTOM_CAPTION_UL_FILE.format(newname=file_name)
        download_location = Config.DOWNLOAD_LOCATION + "/"

        sendmsg = await bot.send_message(
            chat_id=message.chat.id,
            text=script.DOWNLOAD_START,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Cancel", callback_data="cancel")]]),
            reply_to_message_id=message.message_id
        )
        trace_msg = None
        if Config.TRACE_CHANNEL:
            try:
                file = await media.forward(chat_id=Config.TRACE_CHANNEL)
                trace_msg = await file.reply_text(f'**User Name:** {message.from_user.mention(style="md")}\n\n**User Id:** `{message.from_user.id}`\n\n**New File Name:** `{file_name}`\n\n**Status:** Downloading....')
            except PeerIdInvalid:
                logger.warning("Give the correct Channel or Group ID.")
            except ChannelInvalid:
                logger.warning("Add the bot in the Trace Channel or Group as admin to send details of the users using your bot")
            except Exception as e:
                logger.warning(e)
        
        c_time = time.time()
        the_real_download_location = await bot.download_media(
            message=media,
            file_name=download_location,
            progress=progress_for_pyrogram,
            progress_args=(
                script.DOWNLOAD_START,
                sendmsg,
                c_time
            )
        )
        if the_real_download_location is not None:
            try:
                await bot.edit_message_text(
                    text=script.SAVED_RECVD_DOC_FILE,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id
                )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(script.SAVED_RECVD_DOC_FILE, quote=True)

            new_file_name = download_location + file_name + "." + extension
            os.rename(the_real_download_location, new_file_name)
            try:
                await bot.edit_message_text(
                    text=script.UPLOAD_START,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id
                    )
            except:
                await sendmsg.delete()
                sendmsg = await message.reply_text(script.UPLOAD_START, quote=True)
            else:
                if trace_msg:
                    await trace_msg.edit(f'**User Name:** {message.from_user.mention(style="md")}\n\n**User Id:** `{message.from_user.id}`\n\n**New File Name:** `{file_name}`\n\n**Status:** Uploading')
    
            # logger.info(the_real_download_location)

            thumb_image_path = download_location + str(message.from_user.id) + ".jpg"
            if not os.path.exists(thumb_image_path):
                mes = await thumb(message.from_user.id)
                if mes != None:
                    m = await bot.get_messages(message.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path
                else:
                    try:
                        thumb_image_path = await take_screen_shot(new_file_location, os.path.dirname(os.path.abspath(new_file_location)), random.randint(0, duration - 1))
                    except Exception as e:
                        logger.error(e)
                        thumb_image_path = None              
            else:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                img.resize((320, height))
                img.save(thumb_image_path, "JPEG")

            c_time = time.time()
            await bot.send_document(
                chat_id=message.chat.id,
                document=new_file_file_location,
                thumb=thumb_image_path,
                caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=message.reply_to_message.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    script.UPLOAD_START,
                    sendmsg, 
                    c_time
                )
            )

            try:
                os.remove(new_file_name)
                os.remove(thumb_image_path)
            except:
                pass  
            try:
                await bot.edit_message_text(
                    text=script.AFTER_SUCCESSFUL_UPLOAD_MSG,
                    chat_id=message.chat.id,
                    message_id=sendmsg.message_id,
                    disable_web_page_preview=True
                )
            except:
                await sendmsg.delete()
                await message.reply_text(script.AFTER_SUCCESSFUL_UPLOAD_MSG, quote=True)    
            else:
                if trace_msg:
                    await trace_msg.edit(f'**User Name:** {message.from_user.mention(style="md")}\n\n**User Id:** `{message.from_user.id}`\n\n**New File Name:** `{file_name}`\n\n**Status:** Uploaded Sucessfully')          
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You're B A N N E D",
            reply_to_message_id=message.message_id
        )

async def cancel_progress(bot, update):
    
    await bot.sendmsg.stop_message(
        chat_id=update.chat.id,
        text="Process Cancelled 🙃",
    )


