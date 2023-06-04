import logging
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import PollAnswer
import asyncio
import csv
from random import shuffle

# csv таблица для хранения данных ответа юзеров. Содержит никнейм (не обязательно использовать), 
# номер вопроса (колонка принимает 1 если верно, и 0 если нет) и общее кол-во правильных ответов.
fields = ['UserID', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Total']
filename = 'quiz.csv'
with open(filename, 'w') as data:
    csvwriter = csv.writer(data)
    csvwriter.writerow(fields)

# база вопросов. Нужно хотя бы 15 штук
# QuestionList = список со всеми вопросами
with open('QuestionList.txt', 'r', encoding='utf-8') as file:
    QuestionList = file.readlines()
QuestionList = [q.strip() for q in QuestionList]

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
    Answered = State()

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext) -> None:
    print('uno')
    await state.update_data(START='some_data')
    await Form.Started.set()

@dp.message_handler(state=Form.Started)
async def introduction(message: types.Message, state: FSMContext):
    print('dos')
    data = await state.get_data()
    await state.update_data()
    # Создаем кнопки для выбора темы
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*["Омск 1860-1880гг.", "Омск 1890-е", "Омск и ЖД-пути", "Сыграть в квиз"])
    hello_msg = "Привет! Этот бот поможет тебе получить больше знаний о городе Омск в дореволюционной России, а также проверить знания. Для начала можно ознакомиться с историей города по одной из выбранных тем:"
    await message.answer(f"{hello_msg}", reply_markup=keyboard)
    await Form.Informational.set()


# Обработка нажатий на кнопки
@dp.message_handler(content_types=types.ContentTypes.TEXT, state = Form.Informational)
async def handle_buttons(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data()
    if message.text == "Омск 1860-1880гг.":
        await send_info_message(message.chat.id, "Тема 1")
    elif message.text == "Омск 1890-е":
        await send_info_message(message.chat.id, "Тема 2")
    elif message.text == "Омск и ЖД-пути":
        await send_info_message(message.chat.id, "Тема 3")
    elif message.text == "Сыграть в квиз":
        await Form.Quizzed.set()



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
    print('tres')
    data = await state.get_data()
    await state.update_data()
    # перемешиваем вопросы и выбираем 10 штук
    shuffle(QuestionList)
    QuestionSelected = QuestionList[:10]
    global answers
    answers = [] # Сюда по идее записываются ответы, для csv

    for i, question in enumerate(QuestionSelected, start=1): # отправка выбранных вопросов
        question = question.split('/')

        poll = await bot.send_poll(
            message.chat.id,
            question[2],
            options = question[3:],
            type='quiz',
            correct_option_id = question[1],
            is_anonymous = False, # нужно чтобы работал хендлер @dp.poll_answer_handler
            allows_multiple_answers = False,
            reply_to_message_id=message.message_id
            )
        
        answers.extend([poll.poll.id, question[0], question[1], question[2]])
        await asyncio.sleep(1)

    await Form.Informational.set()

# Обработка ответов юзера и последующее занесение в csv        
userdata = []
@dp.poll_answer_handler()
async def handle_poll_answer(poll_answer: types.PollAnswer):
    global answers
    global userdata
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    option_ids = poll_answer.option_ids

    if len(userdata) == 0:
        userdata.append(user_id)

    print(userdata)

    if len(userdata) <= 5:
        zhopa = [str(option_ids[0]), answers[answers.index(poll_id)+2]]
        if zhopa[0] != zhopa[1]:
            userdata.append(0)
        else:
            userdata.append(1)

    else:
        with open(filename, 'w') as data:
            csvwriter = csv.writer(data)
            userdata.append(sum(userdata[1:5]))
            csvwriter.writerow(userdata)
            userdata = []




if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
