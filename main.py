import logging


from aiogram import Bot, Dispatcher, executor, types

from gan_style_transfer import generate_image, init
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Создать глобального бота
bot = Bot(
    token='',
)
dp = Dispatcher(
    bot=bot,
)
artist_weight = {}
artist_names = ['cezan','monet','ukyo','vango','ident']
init()

async def init_dict(user_id):
    artist_weight[user_id] = {'cezan': 0.0,'monet': 0.0,
                              'ukyo': 0.0,'vango': 0.0,'ident': 0.0}

async def remover(orig_path,  result_path):
    os.remove(orig_path)
    os.remove(result_path)

@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    #Код для сохранения изображения в объект
    user_id = message.from_user.id
    if user_id not in artist_weight:
        init_dict(user_id)
    orig_name = 'orig%.d.jpg' %user_id
    result_name = 'result%.d.jpg' %user_id

    await message.photo[0].download(orig_name)
    user_weight = artist_weight[user_id]
    transformed_image = generate_image(user_weight['vango'], user_weight['ukyo'],
                                       user_weight['monet'], user_weight['cezan'],
                                       user_weight['ident'], orig_name)

    transformed_image.save(result_name)
    f = open(result_name, 'rb')
    await bot.send_photo(user_id, f, 'result')
    f.close()
    await remover(orig_name, result_name)

async def add_weight(user_id, value, artist):
    # Установить веса каждого художника
    if user_id not in artist_weight:
        await init_dict(user_id)
    artist_weight[user_id][artist] = value



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Поприветствовать
    await message.reply("Привет!\nУстанови веса для каждого художника или оставь их равными 0."
                        "Установка весов проивзодится командой имя художника пробел значение\n"
                        "Можно выбрать из cezan, ident, vango, ukyo, monet. "
                        "Интервал от 0 до 1")


@dp.message_handler(content_types=types.ContentType.TEXT)
async def do_echo(message: types.Message):
    text = message.text
    try:
        command, value = text.split()
        if command not in artist_names:
            await message.reply('Неверная команда')
        elif (0 > float(value)) | (float(value) > 1):
            await message.reply('Неверное значение')
        else:
            await add_weight(message.from_user.id, float(value), command)
    except Exception:
        await message.reply('Неверная команда')


def main():
    executor.start_polling(
        dispatcher=dp,
    )


if __name__ == '__main__':
    main()
