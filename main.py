from pyrogram import Client
from remove_bg_api import RemoveBg
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors.exceptions import UserNotParticipant
import os
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


from config import Config
from database import Data


app = Client("Remove_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN)



def joined():

    def decorator(func):

        async def wrapped(client, message : Message):

            try:
                check = await app.get_chat_member("SJ_Bots", message.from_user.id)
                if check.status in ['member','administrator','creator']:
                    await func(client, message)
                else:
                    await message.reply("💡 You must join our channel in order to use this bot",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))
            except UserNotParticipant as e:
                await message.reply("💡 You must join our channel in order to use this bot",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("JOIN CHANNEL", url="https://t.me/SJ_Bots")]]))

        return wrapped

    return decorator


@app.on_message(filters.command("start"))
@joined()
async def start(client, message : Message):
    await message.reply(f"𝗛𝗲𝗹𝗹𝗼 @{message.from_user.username},\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "This bot can remove background of any image\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "𝗨𝘀𝗲 /help to know more\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n"
                        "✅𝗖𝗥𝗘𝗗𝗜𝗧𝗦:- @SJ_Bots\n"
                        "➖➖➖➖➖➖➖➖➖➖➖➖\n")
    
    check = await Data.is_in_db(message.from_user.id)
    if check == False:
        await Data.add_new_user(message.from_user.id)


@app.on_message(filters.command("help"))
@joined()
async def help(client, message : Message):
    await message.reply("HELP MENU\n\n"
                        "**COMMANDS**\n"
                        "/start - Restarts The Bot\n"
                        "/help - Send This Help Menu\n\n"
                        "**Send any Image as file to Remove Background**\n\n"
                        "@SJ_Bots")


@app.on_message(filters.document)
@joined()
async def rem_bg(client, message : Message):
    try:
        msg = await message.reply("Downloading your image...")
        img = await message.download()
        # name, extension = os.path.splitext(img)
        await msg.edit("Removing Background...")
        rmbg = RemoveBg(Config.REMOVE_BG_TOKEN)
        rem_img = rmbg.remove_bg_file(img, f"{img}_removed.png")
        with open(f"{img}_removed.png", "wb") as f:
            f.write(rem_img)
        await message.reply_document(f"{img}_removed.png", 
                        caption="HERE IS YOUR IMAGE WITH REMOVED BACKGROUND\n@SJ_Bots")

        await msg.delete()

        os.remove(img)
        os.remove(f"{img}_removed.png")
    except Exception as e:
        await message.reply(e)


@app.on_message(filters.command("stats"))
async def stats(client, message : Message):
    count = await Data.count_users()
    await message.reply(f"**STATS**\n\n**Total Users** : {count}")


@app.on_message(filters.command("broadcast") & filters.reply)
async def stats(client, message : Message):
    users = await Data.get_user_ids()
    tmsg = message.reply_to_message.text.markdown

    msg = await message.reply("Broadcast started")

    fails = 0
    success = 0

    for user in users:
        try:
            await app.send_message(int(user), tmsg)
            success += 1
        except:
            fails += 1

        quotient = (fails + success)/len(users)
        percentage = float(quotient * 100)
        await msg.edit(f"**Broadcast started**\n\nTotal Users : {len(users)}\nProgress : {percentage} %")

    await msg.edit(f"Broadcast Completed**\n\nTotal Users : {len(users)}\nSuccess : {success}\nFails : {fails}")
    



app.run()
