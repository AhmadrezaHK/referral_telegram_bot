from telegram.ext import Filters
import telegram.ext
from unidecode import unidecode
from position import getPositionList
import os
from db import insertDB
from googleapiclient.http import MediaFileUpload
from createService import service
import telegram
from initData import candidate_info
from contacts import check_contact
from position import getPositionList
from folders import FOLDER_LIST


def findNextStep(name):
    for index, state in enumerate(states):
        if(state['key'] == name):
            if(index+1 == len(states)):
                return 0
            else:
                return states[index + 1]


def start(update, context):
    states[0]['prepare-function'](update, context)
    return states[0]['value']


def generateCallback(name):
    def callback(update, context):
        getData(name, update, context)
        nextStep = findNextStep(name)
        if(nextStep['key'] == 'GET_POSITION' and not candidate_info["name"]):
            return nextStep['value'] - 1
        nextStep['prepare-function'](update, context)
        return nextStep['value']
    return callback


def getData(stateName, update, context):
    if(stateName == 'GET_PHONE'):
        candidate_info["referrer"] = unidecode(update.message.text)
        candidate_info["name"] = check_contact(candidate_info["referrer"])

    elif(stateName == 'GET_POSITION'):
        candidate_info["position"] = update.callback_query.data
    elif(stateName == 'GET_RESUME'):
        context.bot.get_file(update.message.document).download(
            'resume/'+update.message.document.file_name)

        file_metadata = {'name': update.message.document.file_name,
                         'parents': [FOLDER_LIST[candidate_info["position"].split("---")[0]]]
                         }
        media = MediaFileUpload('resume/'+update.message.document.file_name,
                                mimetype=update.message.document.mime_type)
        file = service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()

        candidate_info["resume_id"] = file.get('id')

        if os.path.exists("resume/" + update.message.document.file_name):
            os.remove("resume/" + update.message.document.file_name)

    elif(stateName == 'GET_COMMENT'):
        candidate_info["comment"] = update.message.text
        finish()
        update.message.reply_text(
            'ممنون',
        )
        telegram.Bot(token='BOT_TOKEN').sendMessage(
            chat_id=-1001420837511,
            text=str(candidate_info),
        )


def generatePrepareState(stateName):
    def prepareState(update, context):
        if(stateName == 'GET_PHONE'):
            update.message.reply_text(
                'سلام :)) \n ما یعنی تیم منابع انسانی یکتانت خیلی خیلی ممنونیم قصد داری یه آدم خفن برای اضافه شدن به خانواده ی یکتانت بهمون معرفی کنی! این یه کمک بزرگه که باعث میشه روز به روز خفن تر بشیم. لطفا شماره موبایلی که شرکت ازت داره رو برای اعتبارسنجی وارد کن:\n ',
            )
        elif(stateName == 'GET_POSITION'):
            positions = getPositionList()
            keyboard = []

            for x in range(0, len(positions)):
                positions[x] = telegram.InlineKeyboardButton(
                    text=positions[x]["name"], callback_data=positions[x]["name"] + "---" + positions[x]["type"])
            for i in range(0, len(positions), 2):
                keyboard.append(positions[i:i + 2])

            update.message.reply_text(text='این فرد رو برای کدوم پوزیشن در نظر گرفتی؟ اگه تو لیست پوزیشنی که مورد نظرته نیست. لطفا یکی از گزینه های other- Technical یا other - Business رو انتخاب کن.',
                                      reply_markup=telegram.InlineKeyboardMarkup(inline_keyboard=keyboard))
        elif(stateName == 'GET_RESUME'):
            update.callback_query.message.reply_text(
                candidate_info["name"] + 'عزیز \n'
                'لطفا تو این مرحله فایل رزومه ی کسی که میخوای معرفی کنی رو با فرمت پی دی اف بفرست',
            )
        elif(stateName == 'GET_COMMENT'):
            update.message.reply_text(
                'اینکه چرا ایشون رو انتخاب کردی تا  برای این پوزیشن به ما پیشنهاد بدی خیلی مهمه! لطفا در قالب یک پیام در مورد ویژگی های برجسته ی این فرد که با این پوزیشن کاری هم مرتبط هست بهمون بگو:',
            )
    return prepareState


def finish():
    insertDB(candidate_info)


states = [
    {
        'key': 'GET_PHONE',
        'value': None,
        'handler': 'MessageHandler',
        'filter': 'text',
        'callback': generateCallback('GET_PHONE'),
        'prepare-function': generatePrepareState('GET_PHONE')
    },
    {
        'key': 'GET_POSITION',
        'value': None,
        'handler': 'CallbackQueryHandler',
        'filter': None,
        'callback': generateCallback('GET_POSITION'),
        'prepare-function': generatePrepareState('GET_POSITION')
    },
    {
        'key': 'GET_RESUME',
        'value': None,
        'handler': 'MessageHandler',
        'filter': 'document',
        'callback': generateCallback('GET_RESUME'),
        'prepare-function': generatePrepareState('GET_RESUME')
    },
    {
        'key': 'GET_COMMENT',
        'value': None,
        'handler': 'MessageHandler',
        'filter': 'text',
        'callback': generateCallback('GET_COMMENT'),
        'prepare-function': generatePrepareState('GET_COMMENT')
    },
]

for index, state in enumerate(states):
    state['value'] = index

handlers = {}
for state in states:
    handlers[state['handler']] = getattr(telegram.ext, state['handler'])


ConversationHandlerState = {}
for state in states:
    if(state['filter']):
        filters = getattr(Filters, state['filter'])
        ConversationHandlerState[state['value']] = [
            handlers[state['handler']](filters=filters, callback=state['callback'])]
    else:
        ConversationHandlerState[state['value']] = [
            handlers[state['handler']](callback=state['callback'])]
