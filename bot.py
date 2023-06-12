import logging
from aiogram import Bot, Dispatcher, types
from aiogram import executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import csv
import pandas as pd
from os import path, remove
from random import shuffle
import matplotlib.pyplot as mpl
import numpy as np

# csv таблица для хранения данных ответа юзеров. Содержит никнейм (не обязательно использовать), 
# номер вопроса (колонка принимает 1 если верно, и 0 если нет) и общее кол-во правильных ответов.
fields = ['UserID', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Total']
fileres = 'userdata.csv'
if not path.exists(fileres):
    with open(fileres, 'w', newline='') as data:
        csvwriter = csv.writer(data)
        csvwriter.writerow(fields)

# база вопросов. Нужно хотя бы 15 штук
# QuestionList = список со всеми вопросами
QuestionList =[]
filequest = 'QuestionList.csv'
with open(filequest, 'r', newline='', encoding='utf8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            question = [
                row['номер вопроса'],
                row['номер правильного ответа'],
                row['вопрос'],
                row['вариант 1'],
                row['вариант 2'],
                row['вариант 3'],
                row['вариант 4']
            ]
            QuestionList.append(question)

# Устанавливаем уровень логов для отладки
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер
bot = Bot(token="6260709561:AAH6Cr8Cr_KxTRSbd3FCKUl-EP5PrMrsDUk")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# состояние ожидания
class Form(StatesGroup):
    Informational = State() # стейт выбора информации
    Quizzed = State() # стейт прохождения квиза
    Stats = State() # стейт просмотра статистики

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message, state: FSMContext) -> None:
    global keyboard
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*["Посмотреть информацию про город Омск", "Сыграть в квиз", "Посмотреть статистику"])
    hello_msg = "Привет! Этот бот поможет тебе получить больше знаний о городе Омск в дореволюционной России, а также проверить знания. Для начала можно ознакомиться с историей города по одной из выбранных тем:"
    await message.answer(f"{hello_msg}", reply_markup=keyboard)
    await Form.Informational.set()


# Обработка нажатий на кнопки
@dp.message_handler(content_types=types.ContentTypes.TEXT, state = Form.Informational)
async def handle_buttons(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data()
    if message.text == "Посмотреть информацию про город Омск":
        await send_info_message(message.chat.id, "Информация")
    elif message.text == "Сыграть в квиз":
        await start_quiz(message, state=Form.Quizzed)
    elif message.text == "Посмотреть статистику":
        await show_stats(message, state = Form.Stats)



# Функция для отправки информационного сообщения по выбранной теме
async def send_info_message(chat_id: int, topic: str):
    # Здесь можно заполнить информацию по каждой теме
    if topic == "Информация":
        info = "http://omskvinostranihtravelogah.tilda.ws/"
    await bot.send_message(chat_id, info)

# Команда /quiz
@dp.message_handler(state = Form.Quizzed)
async def start_quiz(message: types.Message, state: FSMContext):
    # перемешиваем вопросы и выбираем 5 штук
    shuffle(QuestionList)
    QuestionSelected = QuestionList[:5]
    global answers
    answers = [] # айди опроса, порядковый номер, правильный ответ, текст вопроса
    for i, question in enumerate(QuestionSelected, start=1): # отправка выбранных вопросов
        # question = question.split('/')

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
    # userdata нужна для занесения результатов пользователя, а именно: айди, отвеченные вопросы, итоговое кол-во баллов
    user_id = poll_answer.user.id
    poll_id = poll_answer.poll_id
    option_ids = poll_answer.option_ids

    if len(userdata) == 0:
        userdata.append(user_id)

    if len(userdata) <= 6: # если пользователь ответил не на все ответы, то проходит сравнение ответа пользователя и полученным из answers правильным ответом
                           # 1 если верный ответ, 0 если неверный
        tempor = [str(option_ids[0]), answers[answers.index(poll_id)+2]]
        if tempor[0] != tempor[1]:
            userdata.append(0)
        else:
            userdata.append(1)

    if len(userdata) == 6: # в случае прохождения всех вопросов, данные записываются в csv
        with open(fileres, 'a') as data:
            csvwriter = csv.writer(data)
            userdata.append(sum(userdata[1:]))
            csvwriter.writerow(userdata)
            userdata = []

@dp.message_handler(content_types=types.ContentTypes.TEXT, state = Form.Stats)
async def show_stats(message: types.Message, state: FSMContext):
    user_id = message.from_user.id # айди находится из отправленного сообщения юзером, это нужно для нахождения его данных в таблице

    data = pd.read_csv(fileres)
    user_data = data[data['UserID'] == user_id]

    if user_data.empty:
        await message.answer("Похоже, что Вы ни разу не проходили квиз")
        await Form.Informational.set()
        return

    last_score = user_data['Total'].iloc[-1]
    average_score = user_data['Total'].mean()
    other_users_average = data[data['UserID'] != user_id]['Total'].mean()
    first_attempt_score = user_data['Total'].iloc[0]

    if user_data.shape[0] == 1:
        await message.answer(f"Вы проходили квиз всего один раз и набрали {first_attempt_score} баллов. Это отличается на {first_attempt_score-other_users_average} среднего балла других пользователй.")
    else:
        await message.answer(f"Вот что известно о Ваших прохождениях квиза:\nСредний балл равен {average_score:.2f}, что на {average_score - other_users_average:.2f} отличается от среднего балла остальных пользователей.\nЗа первый тест вы набрали {first_attempt_score} балл. Результат последнего прохождения квиза - {last_score}.")
        attempts = range(1, len(user_data)+1) # нумерация попыток юзера
        
        # Построение графика
        fig, ax = mpl.subplots()
        ax.plot(attempts, user_data['Total'], linewidth=2.0)
        mpl.xticks(attempts)
        mpl.yticks(range(1, 6))
        ax.set(xlabel='Номер попытки', ylabel='Количество баллов',
        xlim=(1, len(user_data['Total'])), ylim=(min(user_data['Total']), max(user_data['Total'])))
        mpl.savefig('quiz_res.png')
        mpl.close

        # Отправка юзеру графика в личные сообщения
        photo = types.InputFile('D:\proj\Labs\quiz_res.png')
        await bot.send_photo(message.chat.id, photo)
        remove('quiz_res.png')

    await Form.Informational.set()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
