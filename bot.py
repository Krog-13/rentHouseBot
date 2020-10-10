from aiogram.dispatcher import filters

import config
import logging
import asyncio
from filter import Filter
from sqlliter import SQLiter
from aiogram import Bot, Dispatcher, types, executor
from ParseOlx import OlX
from aiogram.dispatcher.filters import BoundFilter
FILTERS = []
county_for_db = {'Петропавл':'petropavlovsk','Кустанай':'kostanay', 'Павлодар':'pavlodar'}
county_for_u = {'petropavlovsk':'Петропавл','kostanay':'Кустанай', 'pavlodar':'Павлодар'}
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
    item1 = types.InlineKeyboardButton("Петропавл", callback_data='Петропавл')
    item2 = types.InlineKeyboardButton('Кустанай', callback_data='Кустанай')
    item3 = types.InlineKeyboardButton('Павлодар', callback_data='Павлодар')
    #item4 = types.InlineKeyboardButton('Павлодар', callback_data='Pavlodar')
    #item5 = types.InlineKeyboardButton('Алмата', callback_data='Almata')
    #item6 = types.InlineKeyboardButton('Уральск', callback_data='Uralsk')
    #item7 = types.InlineKeyboardButton('Кокчетав', callback_data='Kokchetav')
    #item8 = types.InlineKeyboardButton('Актобе', callback_data='Aktobe')
    #item9 = types.InlineKeyboardButton('Караганда', callback_data='Karaganda')
    markup.add(item1, item2, item3)
    await message.answer('Выберете город', reply_markup=markup)

#@dp.message_handler(lambda message: message.text and 'hello' in message.text.lower())
@dp.message_handler(regexp='(^[0-9]*[0-9]$)')
async def my_filter(message: types.Message):
    # добавление фильтров в БД
    def add_filter_db(param):
        paramUrl = FL.url_data(param)
        if paramUrl:
            db.add_filters(message.from_user.id, paramUrl)
            return True
        else:
            return False

    if FILTERS:
        FILTERS.append(message.text)
        if not FILTERS[1].isdigit():
            FILTERS.clear()
            await message.answer('введены некорректные данные\n'
                                 'попробуйте еще раз')
        elif len(FILTERS) == 2:
            await message.answer('<em>введите цену до</em>:', parse_mode='html')
        elif len(FILTERS) == 3:
            if (int(FILTERS[2]) - int(FILTERS[1])) > 0 and FILTERS[0].isalpha():
                if add_filter_db(FILTERS):
                    await message.answer('<strong>Фильтр успешно добавлен</strong>\n'
                                     'Город: <b>{}</b>\nЦена от: <b>{}</b> тг\nЦена до: <b>{}</b> тг'
                                     ''.format(county_for_u[FILTERS[0]], FILTERS[1], FILTERS[2]), parse_mode='html')
                    FILTERS.clear()# Every onese is a while
                else:
                    await message.answer('Error 500\n'
                                         'support @Krog_95')
            else:
                FILTERS.clear()
                await message.answer('введены некорректные данные\n'
                                     'попробуйте еще раз')
                FILTERS.clear()
        elif len(FILTERS) > 3:
            FILTERS.clear()
            await message.answer('введены некорректные данные\n'
                                 '<u>попробуйте еще раз</u>', parse_mode='html')
    else:
        await message.answer('Если хотите добавить фильтр\n'
                             'используйте <u>/filter</u>', parse_mode='html')



@dp.message_handler(regexp='([a-z])')
async def unsubscribe(message: types.Message):
    if FILTERS:
        await message.answer('Введен некорректный формат: \n '
                         '<b>вводите только цифры</b>', parse_mode='html')
    else:
        await message.answer('Если хотите добавить фильтр\n'
                             'используйте <u>/filter</u>', parse_mode='html')



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
            dataTown = sg.get_lastKey(town[0], KEYSI)
            db.add_post(dataTown, town)
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
            if call.data in ['Петропавл', 'Кустанай', 'Павлодар', 'Астана', 'Almata', 'Uralsk', 'Karaganda']:
                FILTERS.append(county_for_db[call.data])
                # remove inline buttons
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text='Вы выбрали город {}\n'
                                                 'укажите диапазон (<u>цена от</u>  <u>цена до</u>) \n \n'
                                                 '<em>введите цену от</em>:'.format(FILTERS[0])
                                            , reply_markup=None, parse_mode='html')


            # show alert
            await bot.answer_callback_query(callback_query_id=call.id, show_alert=False,text="")


    except Exception as e:
        print(repr(e))

# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(1800))
    executor.start_polling(dp, skip_updates=True)