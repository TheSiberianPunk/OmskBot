import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import csv
import random

# csv таблица для хранения данных ответа юзеров. Содержит никнейм (не обязательно использовать), 
# номер вопроса (колонка принимает 1 если верно, и 0 если нет) и общее кол-во правильных ответов.
fields = ['Nickname', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Total']
filename = 'quiz.csv'
with open(filename, 'w') as data:
    csvwriter = csv.writer(data)
    csvwriter.writerow(fields)

# база вопросов. Нужно хотя бы 15 штук
# QuestionList = список со всеми вопросами
with open('QuestionList.txt', 'r', encoding='utf-8') as file:
    QuestionList = file.readlines()
QuestionList = [q.strip() for q in QuestionList]
print(QuestionList)

# Устанавливаем уровень логов для отладки
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token="6008903319:AAG1qxQJ-bYelMn1fIhcDRDd-y91sdZ8rsg")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# состояние ожидания
class Form(StatesGroup):
    Started = State()
    Informational = State()
    Quizzed = State()

# Команда /start
@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Form.Started)
    

'''@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_start(message: types.Message):
    if message.text == '/start':
        await introduction(message)
    else:
        await message.answer("Пожалуйста, напишите /start для начала работы.")'''

@dp.message_handler(state=Form.Started)
async def introduction(message: types.Message, state: FSMContext):
    # Создаем кнопки для выбора темы
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*["Омск 1860-1880гг.", "Омск 1890-е", "Омск и ЖД-пути", "Сыграть в квиз"])
    hello_msg = "Привет! Этот бот поможет тебе получить больше знаний о городе Омск в дореволюционной России, а также проверить знания. Для начала можно ознакомиться с историей города по одной из выбранных тем:"
    await message.answer(f"{hello_msg}", reply_markup=keyboard)
    await state.set_state(Form.Informational)


# Обработка нажатий на кнопки
@dp.message_handler(content_types=types.ContentTypes.TEXT, state = Form.Informational)
async def handle_buttons(message: types.Message, state: FSMContext):
    if message.text == "Омск 1860-1880гг.":
        await send_info_message(message.chat.id, "Тема 1")
    elif message.text == "Омск 1890-е":
        await send_info_message(message.chat.id, "Тема 2")
    elif message.text == "Омск и ЖД-пути":
        await send_info_message(message.chat.id, "Тема 3")
    elif message.text == "Сыграть в квиз":
        await state.set_state(Form.Quizzed)



# Функция для отправки информационного сообщения по выбранной теме
async def send_info_message(chat_id: int, topic: str):
    # Здесь можно заполнить информацию по каждой теме
    if topic == "Тема 1":
        info = "ПЛЕЙСХОЛДЕР ССЫЛКИ 1"
    elif topic == "Тема 2":
        info = "ПЛЕЙСХОЛДЕР ССЫЛКИ 2"
    elif topic == "Тема 3":
        info = "ПЛЕЙСХОЛДЕР ССЫЛКИ 3"

    await bot.send_message(chat_id, info)


# Команда /quiz
@dp.message_handler(state = Form.Quizzed)
async def start_quiz(message: types.Message, state: FSMContext):
    # перемешиваем вопросы и выбираем 10 штук
    random.shuffle(QuestionList)
    QuestionSelected = QuestionList[:10]
    
    answers = [] # Сюда по идее записываются ответы, для csv
    for i, question in enumerate(QuestionSelected, start=1):
        poll = await bot.send_poll(
            message.chat.id,
            question,
            options = ['Вариант 1','Вариант 2','Вариант 3','Вариант 4'],
            type='quiz',
            correct_option_id = 1,
            is_anonymous = True,
            allows_multiple_answers = False,
            reply_to_message_id=message.message_id
            )
        answers.append((poll.poll.id, question))
        await asyncio.sleep(1)
        


# Обработка нажатий на кнопки викторины (НЕАКТУАЛЬНО, ЭТО РАБОТАЛО С КОЛБЕК КНОПКАМИ)
@dp.callback_query_handler(lambda c: c.data.startswith('answer_'))
async def process_quiz_answer(callback_query: types.CallbackQuery):
    # Получаем ответ пользователя
    user_answer = callback_query.data.split('_')[1]

    # Здесь можно провести проверку ответа и сохранить результаты для статистики

    await bot.answer_callback_query(callback_query.id, text="Вы выбрали вариант {}".format(user_answer))


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
