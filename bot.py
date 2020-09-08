import config
import logging
import asyncio
from sqlliter import SQLiter
from aiogram import Bot, Dispatcher, types, executor

from ParseOlx import OlX

# Задаем уровень логов
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# inicialization DB
db = SQLiter('olxdb')

# inicialization parser
sg = OlX('Key002.txt')

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

async def scheduled(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        posts  = sg.new_post()
        if(posts):
            posts.reverse()
            for np in posts:
                nfo = sg.post_info(np)
                subscriptions  = db.get_subscriptions()

                for s in subscriptions:
                    photo = open('static/fon.jpg', 'rb')
                    await bot.send_photo(
                        s[1],
                        photo,
                        caption=nfo['title'] + '\n'+'Цена:'+ nfo['prase'] +'От:'+ nfo['who'] +'\nОписание:'+ nfo['disc'].strip()[:400]
                                  +'\nОпубликована '+ nfo['time'] +'\n Ссылка'+ nfo['url'], disable_notification=True)
                    photo.close()

# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(1000)) # пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)