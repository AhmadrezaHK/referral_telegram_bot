from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import logging
from state import ConversationHandlerState, start
from initData import resetDefaultInfo
# from folders import getFolderList


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


updater = Updater(
    'BOT_TOKEN', use_context=True)


def fallback(update, context):
    update.message.reply_text(
        'asd',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[['شروع مجدد']],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )


def reset(update, context):
    resetDefaultInfo()
    return start(update, context)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states=ConversationHandlerState,

    fallbacks=[
        MessageHandler(Filters.regex('^(شروع مجدد)'), reset),
        MessageHandler(Filters.text, fallback),
    ]
)


updater.dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()
