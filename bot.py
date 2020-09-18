import config
import logging
import asyncio
from filter import Filter
from sqlliter import SQLiter
from aiogram import Bot, Dispatcher, types, executor

from ParseOlx import OlX, NEW_KEYS

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
                         'Например F:astana,40000,80000,1,2')
    if (not key_id == 'null'):
        await message.answer('У Вас уже указаны фильры')


@dp.message_handler(regexp='(^F:)')
async def unsubscribe(message: types.Message):
    data = message.text[2:].split(',')
    paramUrl = FL.url_data(data)
    db.add_filters(message.from_user.id, paramUrl)
    if paramUrl:
        #db.update_url(message.from_user.id, paramUrl)
        await message.answer('Фильтр успешно добавлен')
    else:
        await message.answer('Введен некорректный фильтр')





async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        print('START PRE')
        # получаем старые ключи
        keys = db.get_keys()
        KEYSI = [i[0] for i in keys]

        # получаем города
        countries = db.get_country()
        for town in countries:
            print(town)
            dataTown = sg.get_lastKey(town[0], KEYSI)
            db.add_post(dataTown, town)
        if not NEW_KEYS:
            continue
        NEW = tuple(NEW_KEYS)

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

# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(2700))# пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)