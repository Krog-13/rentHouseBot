import config
import logging
import asyncio
from filter import Filter
from sqlliter import SQLiter
from aiogram import Bot, Dispatcher, types, executor
from ParseOlx import OlX

FILTERS = []
testing = []
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
        await message.answer('Вы успешно отписаын от рассылки')

key_id = 'null'
@dp.message_handler(commands=['filter'])
async def unsubscribe(message: types.Message):
    await message.answer('Добавте фильтр в формате (F:город,цена от, цена до)\n'
                         'Например F:astana,40000,80000')

    markup = types.InlineKeyboardMarkup(row_width=3)
    item1 = types.InlineKeyboardButton("Petropavlovsk", callback_data='Petropavlovsk')
    item2 = types.InlineKeyboardButton('Kostanay', callback_data='Kostanay')
    item3 = types.InlineKeyboardButton('Astana', callback_data='Astana')
    item4 = types.InlineKeyboardButton('40000', callback_data= '40000')
    item5 = types.InlineKeyboardButton('50000', callback_data='50000')
    item6 = types.InlineKeyboardButton('60000', callback_data='60')
    item7 = types.InlineKeyboardButton('70000', callback_data='70')
    item8 = types.InlineKeyboardButton('80000', callback_data='80')
    item9 = types.InlineKeyboardButton('90000', callback_data='90')
    print('step')
    markup.add(item1, item2, item3, item4, item5, item6,item7, item8, item9)
    await message.answer('Выберете парамметр для прогноза', reply_markup=markup)

    if (not key_id == 'null'):
        await message.answer('У Вас уже указаны фильры')


@dp.message_handler(regexp='(^F:)')
async def unsubscribe(message: types.Message):
    data = message.text[2:].split(',')
    paramUrl = FL.url_data(data)
    if paramUrl:
        db.add_filters(message.from_user.id, paramUrl)
        #db.update_url(message.from_user.id, paramUrl)
        await message.answer('Фильтр успешно добавлен')
    else:
        await message.answer('Введен некорректный фильтр')


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
            print(type(call.data))
            if call.data in ['Petropavlovsk', 'Kostanay', 'Astana']:
                FILTERS.append(call.data)
                print(FILTERS)
            elif call.data in ['40000', '50000']:
                FILTERS.append(call.data)
                print(FILTERS)

                if len(FILTERS) == 3:
                    if (int(FILTERS[2]) - int(FILTERS[1])) > 0 and FILTERS[0].isalpha():
                        await bot.send_message(call.message.chat.id, 'filter adding {}{}{}'.format(FILTERS[0],FILTERS[1], FILTERS[2]),
                                               parse_mode='html')


            # remove inline buttons
           # await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сегодня ',reply_markup=None)

            # show alert
            #await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
            #                          text="Погода в Петропавловске")

    except Exception as e:
        print(repr(e))



# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(1000))# пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)