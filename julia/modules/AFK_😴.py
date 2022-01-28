import os
from julia import tbot, CMD_HELP
from julia.modules.sql import afk_sql as sql

import time
from telethon import types
from telethon.tl import functions
from julia.events import register

from pymongo import MongoClient
from julia import MONGO_DB_URI
from telethon import events

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["missjuliarobot"]
approved_users = db.approve


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):          
        return True


@register(pattern=r"(.*?)")
async def _(event):
    sender = await event.get_sender()
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return

    if event.text.startswith("/afk"):
        cmd = event.text[len("/afk ") :]
        reason = cmd if cmd is not None else ""
        fname = sender.first_name
        # print(reason)
        start_time = time.time()
        sql.set_afk(sender.id, reason, start_time)
        await event.reply(
              "**{} is now AFK !**".format(fname),
              parse_mode="markdown")
        return

    if sql.is_afk(sender.id):
        if res := sql.rm_afk(sender.id):
            firstname = sender.first_name
            text = "**{} is no longer AFK !**".format(firstname)
            await event.reply(text, parse_mode="markdown")
        

@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    sender = event.sender_id
    msg = str(event.text)
    global let
    global userid
    userid = None
    let = None
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        userid = reply.sender_id
    else:
        try:
            for (ent, txt) in event.get_entities_text():
                if ent.offset != 0:
                    break
                if not isinstance(
                    ent, types.MessageEntityMention
                ) and not isinstance(ent, types.MessageEntityMentionName):
                    return
                c = txt
                a = c.split()[0]
                let = await tbot.get_input_entity(a)
                userid = let.user_id
        except Exception:
            return

    if not userid:
        return
    if sender == userid:
        return

    if not event.is_group:
        return

    if sql.is_afk(userid):
        user = sql.check_afk_status(userid)
        fst_name = "This user"
        etime = user.start_time
        if not user.reason:
            elapsed_time = time.time() - float(etime)
            final = time.strftime("%Hh: %Mm: %Ss", time.gmtime(elapsed_time))
            res = "**{} is AFK !**\n\n**Last seen**: {}".format(fst_name, final)

        else:
            elapsed_time = time.time() - float(etime)
            final = time.strftime("%Hh: %Mm: %Ss", time.gmtime(elapsed_time))
            res = "**{} is AFK !**\n\n**Reason**: {}\n\n**Last seen**: {}".format(
                fst_name, user.reason, final
            )
        await event.reply(res, parse_mode="markdown")
    userid = ""  # after execution
    let = ""  # after execution


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /afk <reason>: mark yourself as AFK(Away From Keyboard)
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})
