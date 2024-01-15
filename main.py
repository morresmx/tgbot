import sqlite3
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    name = State()

# Configure logging
logging.basicConfig(level=logging.INFO)


# Initialize bot and dispatcher
bot = Bot(token='TELEGRAM BOT TOKEN')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=False)
    item1 = types.KeyboardButton('💎 Личный кабинет')
    item2 = types.KeyboardButton('🔎 Прочее инфо')
    markup.add(item1, item2)
    await message.answer('Добро пожаловать в личный кабинет!', reply_markup=markup)

async def send_personal_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('🧡 Вход в MAIS')
    back = types.KeyboardButton('⬅ Назад')
    markup.add(item1, back)
    await message.answer('Добро пожаловать в личный кабинет!', reply_markup=markup)

async def send_other_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('🚌 Городской транспорт')
    back = types.KeyboardButton('⬅ Назад')
    markup.add(item1, back)
    await message.answer('Вся информация тут', reply_markup=markup)


async def send_back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('💎 Личный кабинет')
    item2 = types.KeyboardButton('🔎 Прочее инфо')
    markup.add(item1, item2)
    await message.answer('⬅ Назад', reply_markup=markup)


async def send_transport(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('🚌 Городской транспорт')
    back = types.KeyboardButton('⬅ Назад')
    markup.add(item1, back)

    await message.answer(''' text ''', reply_markup=markup, parse_mode='Markdown')


async def send_mais_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    back = types.KeyboardButton('⬅ Назад')
    markup.add(back)

    db = sqlite3.connect('users.db')
    c = db.cursor()

    people_id = message.chat.id
    c.execute(f"SELECT * FROM mais_users WHERE id = {people_id}")
    data = c.fetchone()

    if data is not None:
        login, password = data[2], data[3]
        await message.answer(f"*Логин*: {login}\n*Пароль*: {password}", reply_markup=markup, parse_mode='Markdown')
    else:
        await message.answer("Информация о ваших учетных данных не найдена.", reply_markup=markup)
    db.close()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Connect DB
    db = sqlite3.connect('users.db')
    c = db.cursor()

    people_id = message.chat.id
    c.execute(f"SELECT id FROM mais_users WHERE id == {people_id}")
    data = c.fetchone()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=False)
    item1 = types.KeyboardButton('💎 Личный кабинет')
    item2 = types.KeyboardButton('🔎 Прочее инфо')
    markup.add(item1, item2)

    if data is None:
        await RegistrationStates.name.set()  # Устанавливаем состояние для получения имени
        await message.answer("Добро пожаловать! Введите ваше имя:")
    else:
        db.close()
        await message.answer(f"Привет *{message.from_user.first_name}*!\n", reply_markup=markup, parse_mode='Markdown')


@dp.message_handler(state=RegistrationStates.name)
async def process_name(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    item1 = types.KeyboardButton('🧡 Вход в MAIS')
    back = types.KeyboardButton('⬅ Назад')
    markup.add(item1, back)

    newname = message.text

    # Connect to DB
    db = sqlite3.connect('users.db')
    c = db.cursor()

    people_id = message.chat.id
    c.execute("SELECT id FROM mais_users WHERE full_name = ?", (newname,))
    data = c.fetchone()

    if data is not None and data[0] != people_id:
        c.execute("UPDATE mais_users SET id = ? WHERE full_name = ?;", (people_id, newname))
        db.commit()
        await message.answer(f"Привет {message.from_user.first_name}! Вы успешно вошли в систему.", reply_markup=markup)
    else:
        await message.answer(f"Привет {message.from_user.first_name}!", reply_markup=markup)

    db.close()
    await state.finish()


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def bot_message_handler(message: types.Message):
    if message.chat.type == 'private':
        if message.text == '💎 Личный кабинет':
            await send_personal_info(message)

        elif message.text == '🔎 Прочее инфо':
            await send_other_info(message)

        elif message.text == '⬅ Назад':
            await send_back(message)

        elif message.text == '🧡 Вход в MAIS':
            await send_mais_info(message)

        elif message.text == '🚌 Городской транспорт':
            await send_transport(message)


async def on_startup(dp):
    await bot.send_message(chat_id='540347680', text='Bot has been started')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(on_startup(dp))
    logging.info("Starting bot polling...")
    executor = dp.start_polling(dp)
    try:
        loop.run_until_complete(executor)
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
