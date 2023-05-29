import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Устанавливаем уровень логов для отладки
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token="6008903319:AAG1qxQJ-bYelMn1fIhcDRDd-y91sdZ8rsg")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
 

# Команда /start
'''@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Для начала работы напишите /start")'''

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_start(message: types.Message):
    if message.text == '/start':
        await introduction(message)
    else:
        await message.answer("Пожалуйста, напишите /start для начала работы.")

    
async def introduction(message: types.Message):
    # Создаем кнопки для выбора темы
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*["Тема 1", "Тема 2", "Тема 3"])
    hello_msg = ["Привет! Этот бот поможет тебе получить больше знаний о городе Омск в дореволюционной России,", 
                 "а также проверить знания. Для начала можно ознакомиться с историей города по одной из выбранных тем:"]
    await message.answer(f"{hello_msg}", reply_markup=keyboard)


# Обработка нажатий на кнопки
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_buttons(message: types.Message):
    if message.text == "Тема 1":
        await send_info_message(message.chat.id, "Тема 1")
    elif message.text == "Тема 2":
        await send_info_message(message.chat.id, "Тема 2")
    elif message.text == "Тема 3":
        await send_info_message(message.chat.id, "Тема 3")


# Функция для отправки информационного сообщения по выбранной теме
async def send_info_message(chat_id: int, topic: str):
    # Здесь можно заполнить информацию по каждой теме
    if topic == "Тема 1":
        info = "Информация по Теме 1"
    elif topic == "Тема 2":
        info = "Информация по Теме 2"
    elif topic == "Тема 3":
        info = "Информация по Теме 3"

    await bot.send_message(chat_id, info)


# Команда /quiz
@dp.message_handler(commands=['quiz'])
async def start_quiz(message: types.Message):
    # Создаем клавиатуру с вариантами ответов
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*[
        types.InlineKeyboardButton(text="Вариант 1", callback_data="answer_1"),
        types.InlineKeyboardButton(text="Вариант 2", callback_data="answer_2"),
        types.InlineKeyboardButton(text="Вариант 3", callback_data="answer_3"),
        types.InlineKeyboardButton(text="Вариант 4", callback_data="answer_4"),
    ])

    # Генерируем случайный вопрос (здесь можно использовать базу вопросов)
    question = "Вопрос по теме: {}?\n\n1. Ответ 1\n2. Ответ 2\n3. Ответ 3\n4. Ответ 4".format("Тема")
    
    # Сохраняем вопрос и правильный ответ в контексте пользователя
    await message.answer(question, reply_markup=keyboard)
    await bot.set_my_commands(types.BotCommand(command='/start', description='Начать бота'))


# Обработка нажатий на кнопки викторины
@dp.callback_query_handler(lambda c: c.data.startswith('answer_'))
async def process_quiz_answer(callback_query: types.CallbackQuery):
    # Получаем ответ пользователя
    user_answer = callback_query.data.split('_')[1]

    # Здесь можно провести проверку ответа и сохранить результаты для статистики

    await bot.answer_callback_query(callback_query.id, text="Вы выбрали вариант {}".format(user_answer))


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
