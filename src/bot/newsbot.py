import bson
import datetime
import html
import json
import logging
import os
import traceback

import pymongo
import telegram
from telegram import ParseMode, Update
from telegram.ext import CommandHandler, ConversationHandler, Updater, MessageHandler, CallbackContext, Filters

DB = pymongo.MongoClient(os.getenv('MONGO_URL', 'mongodb://db:27017/'),
                         username=os.getenv('MONGO_USERNAME'),
                         password=os.getenv('MONGO_PASSWORD'))
DB_NAME = 'posts'
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEVELOPER_CHAT_ID = os.getenv('DEVELOPER_CHAT_ID')

MESSAGE_TYPES_DEFAULTS = [u'медицина', u'жилье', u'помощь', u'транспорт', u'визы']
MESSAGE_TYPES = [s for s in os.getenv('MESSAGE_TYPES', '').split(',') if s.strip()] or MESSAGE_TYPES_DEFAULTS
MESSAGE, SET_TYPE = range(2)

# set up logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def save_post(post_data):
    db = DB[DB_NAME]
    col = db["posts"]
    if '_id' in post_data:
        logger.debug('Found existing entry with id %s', post_data['_id'])
        col.replace_one({'_id': post_data['_id']}, post_data)
        return post_data['_id']
    else:
        res = col.insert_one(post_data)
        logger.debug('Created a new entry %s', res)
        return res.inserted_id


def get_post(post_id):
    db = DB[DB_NAME]
    col = db["posts"]
    res = col.find_one({"_id": bson.ObjectId(post_id)})
    return res


def get_types(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(','.join(MESSAGE_TYPES))


def get_message(update: Update, context: CallbackContext) -> None:
    msg_id = context.args[0] if context.args else ''
    msg = get_post(msg_id)
    if msg:
        update.effective_message.reply_text(f'Type: {msg["type"]}\n{msg["text"]}')
    else:
        update.effective_message.reply_text(f'No message with id {msg_id} found')


def register_message(update: Update, context: CallbackContext) -> None:
    msg = update.effective_message.text
    message = {'text': update.effective_message.text, 'date': datetime.datetime.now(), 'type': ''}
    msg_id = save_post(message)
    if not msg_id:
        # Errors duting message save, can't proceed
        logger.error('Could not save message %s', msg)
        return
    update.effective_message.reply_text(
            f'Saved message to db as {msg_id}.\nTo set type send another message or say skip')
    context.user_data['msg'] = message

    return SET_TYPE


def set_type(update: Update, context: CallbackContext) -> None:
    msg = context.user_data['msg']
    if update.effective_message.text == 'skip':
        update.effective_message.reply_text(
                f'Not setting type, to set later use /settype {msg["_id"]} YOURTYPE')
        return
    msg_type = update.effective_message.text if update.effective_message.text != 'skip' else ''
    msg['type'] = msg_type
    res = save_post(msg)
    update.effective_message.reply_text(f'Set {msg_type} for message {msg["_id"]}')

    return ConversationHandler.END


def set_type_for_message(update: Update, context: CallbackContext) -> None:
    args = [s for s in context.args if s.strip()]
    if len(args) < 2:
        error = 'Not enough arguments: Please pass a message ID and TYPE'
        update.effective_message.reply_text(error)
    else:
        msg_id, msg_type = args[0:2]
        logger.debug('%s, %s', msg_id, msg_type)
        msg = get_post(msg_id)
        logger.debug('msg is %s', msg)
        msg['type'] = msg_type
        save_post(msg)
    update.effective_message.reply_text(f'Set {msg_type} for message {msg_id}')


# NOTE(ivasilev) Shamelessly borrowed from
# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/errorhandlerbot.py
def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def run():
    updater = Updater(TOKEN)
    conv_handler = ConversationHandler(
        states={
            SET_TYPE: [MessageHandler(Filters.text & (~Filters.command | Filters.regex('^skip$')), set_type)],
            },
        fallbacks=[],
        entry_points=[MessageHandler(Filters.text & ~Filters.command, register_message)])
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('types', get_types))
    updater.dispatcher.add_handler(CommandHandler('settype', set_type_for_message))
    updater.dispatcher.add_handler(CommandHandler('message', get_message))
    updater.dispatcher.add_error_handler(error_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    run()
