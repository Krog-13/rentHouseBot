from aiogram.dispatcher import filters

import config
import logging
import asyncio
from filter import Filter
from sqlliter import SQLiter
from aiogram import Bot, Dispatcher, types, executor
from ParseOlx import OlX

FILTERS = []

# Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# inicialization DB
db = SQLiter('olxdb')

# inicialization parser
sg = OlX()
FL = Filter()
# command activations
@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id)
    else:
        db.update_subscription(message.from_user.id, True)
    await message.answer('Вы успешно подписались на рассылку! OLX')

# Команда отписки
@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if(not db.subscriber_exists(message.from_user.id)):
        db.add_subscriber(message.from_user.id, False)
        await message.answer('Вы и так подписаны!')
    else:
        db.update_subscription(message.from_user.id, False)
        await message.answer('Вы успешно отписаны от рассылки')

key_id = 'null'
@dp.message_handler(commands=['filter'])
async def unsubscribe(message: types.Message):

    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton("Petropavlovsk", callback_data='Petropavlovsk')
    item2 = types.InlineKeyboardButton('Kostanay', callback_data='Kostanay')
    item3 = types.InlineKeyboardButton('Astana', callback_data='Astana')
    item4 = types.InlineKeyboardButton('Pavlodar', callback_data='Pavlodar')
    item5 = types.InlineKeyboardButton('Almata', callback_data='Almata')
    item6 = types.InlineKeyboardButton('Uralsk', callback_data='Uralsk')
    item7 = types.InlineKeyboardButton('Kokchetav', callback_data='Kokchetav')
    item8 = types.InlineKeyboardButton('Aktobe', callback_data='Aktobe')
    item9 = types.InlineKeyboardButton('Karaganda', callback_data='Karaganda')
    markup.add(item1, item2, item3, item4, item5, item6,item7, item8, item9)
    await message.answer('Выберете город', reply_markup=markup)
'''
    markupCost = types.InlineKeyboardMarkup(row_width=5)
    item11 = types.InlineKeyboardButton('30000', callback_data='30000')
    item22 = types.InlineKeyboardButton('40000', callback_data='40000')
    item33 = types.InlineKeyboardButton('50000', callback_data='50000')
    item44 = types.InlineKeyboardButton('60000', callback_data='60000')
    item55 = types.InlineKeyboardButton('70000', callback_data='70000')
    item66 = types.InlineKeyboardButton('80000', callback_data='80000')
    item100 = types.InlineKeyboardButton('55000', callback_data='55000')
    item77 = types.InlineKeyboardButton('90000', callback_data='90000')
    item88 = types.InlineKeyboardButton('100000', callback_data='10000')
    item99 = types.InlineKeyboardButton('120000', callback_data='120000')
    markupCost.add(item11, item22, item33, item44, item55, item66, item77, item88, item99, item100)
    await message.answer('Выберете диапазон цен', reply_markup=markupCost)
#добавить диапазон цен и проыерить на isdigit
'''
@dp.message_handler(regexp='(^[0-9]*[0-9]$)')
#@dp.message_handler(regexp='(^F:)')
async def unsubscribe(message: types.Message):
    FILTERS.append(message.text)
    print(FILTERS)
    if FILTERS:
        if not FILTERS[1].isdigit():
            FILTERS.clear()
            await message.answer('введены некорректные данные\n'
                                 'попробуйте еще раз')
        elif len(FILTERS) == 2:
            await message.answer('введите цену до:')
        elif len(FILTERS) == 3:
            if (int(FILTERS[2]) - int(FILTERS[1])) > 0 and FILTERS[0].isalpha():
                FILTERS.clear()
                await message.answer('Фильтр успешно добавлен')
            else:
                await message.answer('введены некорректные данные\n'
                                     'попробуйте еще раз')
                FILTERS.clear()





    '''
    data = message.text[2:].split(',')
    paramUrl = FL.url_data(data)
    if paramUrl:
        db.add_filters(message.from_user.id, paramUrl)
        #db.update_url(message.from_user.id, paramUrl)
        await message.answer('Фильтр успешно добавлен')
    else:
        await message.answer('Введен некорректный фильтр')
'''

async def scheduled(wait_for):
    while True:
        sg.NEW_KEYS.clear()
        await asyncio.sleep(wait_for)
        # получаем старые ключи
        keys = db.get_keys()
        KEYSI = [i[0] for i in keys]

        # получаем города
        countries = db.get_country()
        for town in countries:
            print(town)
            dataTown = sg.get_lastKey(town[0], KEYSI)
            db.add_post(dataTown, town)
        print('tut', sg.NEW_KEYS)
        if not sg.NEW_KEYS:
            continue
        sg.NEW_KEYS.reverse()
        NEW = tuple(sg.NEW_KEYS)

        # новые посты для подписчиков
        paring = db.get_new_post(NEW)
        users_post = {}
        for i, k in paring:
            users_post[k] = []
        for i, k in paring:
            users_post[k].append(i)


 #       await asyncio.sleep(wait_for)
        print('START NOW')
        for site in users_post:
            nfo = sg.post_info(site)
            for user in users_post[site]:
                photo = open('static/fon.jpg', 'rb')
                await bot.send_photo(
                    user,
                    photo,
                    caption=nfo['title'] + '\n' + 'Цена:' + nfo['prase'] + 'От:' + nfo['who'] + '\nОписание:'
                            + nfo['disc'].strip()[:400]
                            + '\nОпубликована ' + nfo['time'] + '\n Ссылка' + nfo['url'], disable_notification=True)
                photo.close()

@dp.callback_query_handler(lambda call: True)
async def inline(call: types.callback_query):
    try:
        if call.message:
            if call.data in ['Petropavlovsk', 'Kostanay', 'Astana', 'Pavlodar', 'Almata', 'Uralsk', 'Karaganda']:
                FILTERS.append(call.data)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text='Вы выбрали город {}\n'
                                                 'укажите диапазон (цена от  цена до) \n'
                                                 'введите цену от:'.format(FILTERS[0])
                                            , reply_markup=None)
                '''
            elif call.data in ['30000','40000', '50000','60000', '70000', '80000', '90000','100000','120000', '55000']:
                FILTERS.append(call.data)

                if len(FILTERS) == 3:
                    if (int(FILTERS[2]) - int(FILTERS[1])) > 0 and FILTERS[0].isalpha():
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                    text='Ваш фильтр: город:{}\n диапазон цен от {} до {}\n'
                                                         'успешно добавлен!'.format(FILTERS[0],FILTERS[1], FILTERS[2]),
                                               reply_markup=None)
                        FILTERS.clear()
                    else:
                        FILTERS.clear()
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                    text='Извените что-то пошло не так попробуйте снова',
                                                    reply_markup=None)
                elif len(FILTERS) == 2:
                    if not (FILTERS[1].isdigit()):
                        FILTERS.clear()
                        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                    text='Извените что-то пошло не так попробуйте снова',
                                                    reply_markup=None)

'''

            # remove inline buttons


            # show alert
            #await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,text="Погода в Петропавловске")


    except Exception as e:
        print(repr(e))




# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(100000))# пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)