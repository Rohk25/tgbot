from telegram import MessageEntity
from telegram.ext import CommandHandler, Filters, MessageHandler, run_async, RegexHandler

from tg_bot import dispatcher
from tg_bot.modules.sql import afk_sql as sql
from tg_bot.modules.users import get_user_id

AFK_GROUP = 7
AFK_REPLY_GROUP = 8


@run_async
def afk(bot, update):
    args = update.effective_message.text.split(None, 1)
    if len(args) >= 2:
        reason = args[1]
    else:
        reason = ""

    sql.set_afk(update.effective_user.id, reason)
    update.effective_message.reply_text("{} is now AFK!".format(update.effective_user.first_name))


@run_async
def no_longer_afk(bot, update):
    user = update.effective_user
    res = sql.rm_afk(user.id)
    if res:
        update.effective_message.reply_text("{} is no longer AFK!".format(update.effective_user.first_name))


@run_async
def reply_afk(bot, update):
    message = update.effective_message
    if message.entities and message.parse_entities([MessageEntity.TEXT_MENTION]):
        entities = message.parse_entities([MessageEntity.TEXT_MENTION])
        for ent in entities:
            user_id = ent.user.id
            user = sql.check_afk_status(user_id)
            if user and user.is_afk:
                if not user.reason:
                    res = "{} is AFK!".format(ent.user.first_name)
                else:
                    res = "{} is AFK! says its because of:\n{}".format(ent.user.first_name, user.reason)
                message.reply_text(res)

    elif message.entities and message.parse_entities([MessageEntity.MENTION]):
        entities = message.parse_entities([MessageEntity.MENTION])
        for ent in entities:
            user_id = get_user_id(message.text[ent.offset:ent.offset + ent.length])
            if not user_id:
                # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?
                return
            user = sql.check_afk_status(user_id)
            if user and user.is_afk:
                chat = bot.get_chat(user_id)
                if not user.reason:
                    res = "{} is AFK!".format(chat.first_name)
                else:
                    res = "{} is AFK!\nReason: {}".format(chat.first_name, user.reason)
                message.reply_text(res)

    else:
        return


__help__ = """
 - /afk <reason>: mark yourself as AFK - any mentions will be replied to with a message to say you're not available!
 - brb <reason>: same as the afk command - but not a command.
"""

__name__ = "AFK"

AFK_HANDLER = CommandHandler("afk", afk)
AFK_REGEX_HANDLER = RegexHandler("(?i)brb", afk)
NO_AFK_HANDLER = MessageHandler(Filters.all, no_longer_afk)
AFK_REPLY_HANDLER = MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION),
                                   reply_afk)

dispatcher.add_handler(AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REGEX_HANDLER, AFK_GROUP)
dispatcher.add_handler(NO_AFK_HANDLER, AFK_GROUP)
dispatcher.add_handler(AFK_REPLY_HANDLER, AFK_REPLY_GROUP)
