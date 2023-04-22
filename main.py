import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
import random
import asyncio
import sqlite3
import json

conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()


def show_count_of_type_task(type_task: int):
    with open(f'task_{type_task}.json', encoding='UTF-8') as file:
        return len(json.load(file))


with open('users.json', 'r') as file:
    USERS = json.load(file)
print(USERS)
type_of_tasks = [9, 10, 11, 12, 15, 16, 17, 18, 19, 20, 21]
TYPE_OF_DATA_USERS = {'type_menu': '',
                      'current_num_accent_word': 0,
                      'current_menu_of_accents': [],
                      'current_task_1': 0,
                      'current_task_2': 0,
                      'current_task_3': 0,
                      'current_task_5': 0,
                      'current_task_6': 0,
                      'current_task_9': 0,
                      'current_task_10': 0,
                      'current_task_11': 0,
                      'current_task_12': 0,
                      'current_task_15': 0,
                      'current_task_16': 0,
                      'current_task_17': 0,
                      'current_task_18': 0,
                      'current_task_19': 0,
                      'current_task_20': 0,
                      'current_task_21': 0,
                      'tasks_complited': [],
                      'score': 0}

ACCENTS = []
with open('accents.txt', mode='r', encoding='UTF-8') as file:
    for i in file:
        item = i.split()[0]
        if not item[-1].isalpha() and item[-1] != ')':
            item = item[:-1]
        ACCENTS.append(item)
all_commands = ['Ударения', 'Пунктуация', 'Орфография', 'Список лидеров', 'Доп. Информация', 'о боте', 'моя статистика']
grammar_commands = ['Задание 9', 'Задание 10', 'Задание 11', 'Задание 12', 'Задание 15',
                    'Задание 16', 'Задание 17', 'Задание 18', 'Задание 19', 'Задание 20', 'Задание 21']

UPDATE_INFO = """
poit - балл, который начисляется за верно решенную задачу.

Что добавлено:
1) Сохранение результатов после ремонта.
2) Добавлены теги пользователей в списке лидеров.
3) За задачу на ударение 1 поинт, за задачу в блоках орфографии и пунктуации по 20 поинтов.

Что планируется быть измененным или добаленным:
1) Количество задач. Сейчас в блоке ударений все слова, но в остальных блоках по 10 штук.
2) Задания на паронимы + 1-3 задачи.

Если возникли вопросы или произошла ошибка, пишите мне ---> @G30rG32

<i><b>Можно еще поддержать автора, чтобы работа шла побыстрее</b></i> 😁:
Сбербанк ---> 5469720013481755 (Георгий Козлов)
"""


async def echo(update, context):
    print(update.message.from_user.first_name)
    user_id = str(update.message.from_user.id)
    with open('users.json', 'w+') as file:
        json.dump(USERS, file)
    if user_id not in USERS:
        return await update.message.reply_html(
            'Бот 🤖 был в ремонте (или в настоящий момент) Некоторые данные могли быть сброшены.\n'
            'Нажмите на это ----> /start , чтобы презапустить его')
    type_menu = USERS[user_id]['type_menu']
    message = update.message.text
    if message in all_commands + grammar_commands or message == 'в главное меню':
        USERS[user_id]['type_menu'] = message
        type_menu = message
    if type_menu == 'Список лидеров':
        await create_list_of_leaders(update)
    if type_menu == 'Ударения':
        await accent_menu(update, message)
    if type_menu == 'Доп. Информация':
        await update.message.reply_html('Доп. Информация', reply_markup=menu_of_add_info())
    if type_menu == 'о боте':
        await update.message.reply_html(UPDATE_INFO, reply_markup=menu_of_add_info())
    if type_menu == 'моя статистика':
        await stat_info(update)
    if type_menu == 'в главное меню':
        await update.message.reply_text('Главное меню:', reply_markup=main_menu_keyboard())
    if type_menu == 'Орфография':
        await update.message.reply_text('Блок орфографии:', reply_markup=menu_of_grammar())
    if type_menu == 'Пунктуация':
        await update.message.reply_text('Блок пунктуации:', reply_markup=menu_of_punctuation())
    if type_menu in grammar_commands and message in grammar_commands:
        await create_task(update, type_task=type_menu)
    if type_menu in grammar_commands and message not in grammar_commands:
        await check_the_correct_answer(update, type_task=type_menu)


def menu_of_add_info():
    keyboard = [['моя статистика'], ['о боте'], ['в главное меню']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    return markup


async def stat_info(user):
    user_id = str(user.message.from_user.id)
    result = ''
    result += f'Решено  <i><b>{USERS[user_id]["current_num_accent_word"]}</b></i>' \
              f' ударений из <i><b>279</b></i>\n'
    for num_tsk in type_of_tasks:
        score = USERS[user_id][f"current_task_{num_tsk}"]
        if str(num_tsk) in USERS[user_id]['tasks_complited']:
            score = show_count_of_type_task(type_task=num_tsk)
        result += f'Решено №{num_tsk} заданий <i><b>{score}</b></i> ' \
                  f'из <i><b>{show_count_of_type_task(type_task=num_tsk)}</b></i>\n'

    await user.message.reply_html(result, reply_markup=menu_of_add_info())


async def create_task(user, type_task):
    user_id = str(user.message.from_user.id)
    num_tsk = type_task.split()[-1]
    with open(f'task_{num_tsk}.json', encoding='UTF-8') as file:
        data = json.load(file)
        await user.message.reply_html(data[USERS[user_id][f'current_task_{num_tsk}']]['task'],
                                      reply_markup=back_to_main_menu())
    await user.message.reply_html('Введите ответ:')


async def check_the_correct_answer(user, type_task):
    num_tsk = type_task.split()[-1]
    user_answer = user.message.text
    user_id = str(user.message.from_user.id)
    with open(f'task_{num_tsk}.json', encoding='UTF-8') as file:
        data = json.load(file)
    id_of_task = USERS[user_id][f'current_task_{num_tsk}']
    correct_answer = data[id_of_task]['answer'].split('или')
    if user_answer in correct_answer:
        if USERS[user_id][f'current_task_{num_tsk}'] + 1 == show_count_of_type_task(int(num_tsk)):
            USERS[user_id]['tasks_complited'].append(num_tsk)
        USERS[user_id][f'current_task_{num_tsk}'] = (USERS[user_id][f'current_task_{num_tsk}'] + 1) % len(data)
        USERS[user_id]['score'] += 20
        await user.message.reply_text('Верно ✅', reply_markup=back_to_main_menu())
        await create_task(user, type_task=type_task)
    else:
        USERS[user_id]['type_menu'] = 'в главное меню'
        await user.message.reply_text('Ошибка ❌', reply_markup=main_menu_keyboard())
        await user.message.reply_html(data[id_of_task]['description'])
        line = ' '.join([i for i in correct_answer])
        await user.message.reply_text(f'Ваш ответ: {user_answer}\nПравильный ответ: {line}')
        await message_about_new_record(user)
        USERS[user_id]['score'] = 0


def back_to_main_menu():
    keyboard = [['в главное меню']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    return markup


async def accent_menu(update, word):
    user_id = str(update.message.from_user.id)
    id_accent_word = USERS[user_id]['current_num_accent_word']
    correct_accent_word = ACCENTS[id_accent_word]
    if word not in all_commands:
        if word == correct_accent_word:
            USERS[user_id]['current_num_accent_word'] = (USERS[user_id]['current_num_accent_word'] + 1) % len(ACCENTS)
            USERS[user_id]['score'] += 1
            await update.message.reply_text('Верно ✅', reply_markup=generate_main_accents_menu(user_id))
        else:
            USERS[user_id]['type_menu'] = 'в главное меню'
            await update.message.reply_text('Ошибка ❌', reply_markup=main_menu_keyboard())
            await update.message.reply_text(f'Правильно: {correct_accent_word}')
            await message_about_new_record(update)

    else:
        await update.message.reply_text('Выберите ударение:', reply_markup=generate_main_accents_menu(user_id))


def generate_main_accents_menu(user_id):
    menu_of_accents = create_accents_words(user_id=user_id) + [['в главное меню']]
    random.shuffle(menu_of_accents[0])
    USERS[user_id]['current_menu_of_accents'] = menu_of_accents[0]
    markup = ReplyKeyboardMarkup(menu_of_accents, one_time_keyboard=False, resize_keyboard=True)
    return markup


def create_accents_words(user_id):
    id_of_accent_word = USERS[user_id]['current_num_accent_word']
    correct_word = ACCENTS[id_of_accent_word]
    incorrect_word = create_incorrect_word(correct_word)
    line_words = [[correct_word, incorrect_word]]
    return line_words


def create_incorrect_word(correct_word):
    index_correct_word = None
    for i in range(len(correct_word)):
        if correct_word[i].isupper():
            index_correct_word = i
            break
    word_per_letter = list(correct_word.lower())
    index_vowels = []
    for i, j in enumerate(word_per_letter, 0):
        if j == '(':
            break
        if j in 'ауоыиэяюёе' and i != index_correct_word:
            index_vowels.append(i)
    index = index_vowels[random.randint(0, len(index_vowels) - 1)]
    word_per_letter[index] = word_per_letter[index].upper()
    incorrect_word = ''.join(word_per_letter)
    return incorrect_word


async def start(update, context):
    us_id = str(update.message.from_user.id)
    us_name = update.message.from_user.first_name
    us_sname = update.message.from_user.last_name
    username = update.message.from_user.username
    result = cursor.execute(f'SELECT * FROM user_data WHERE User_id = {us_id}').fetchall()
    user = update.effective_user
    print(user.mention_html())
    if us_id not in USERS:
        USERS[us_id] = TYPE_OF_DATA_USERS
    if len(result) != 0:
        await update.message.reply_html(
            f"{user.mention_html()}, Добро пожаловать!", reply_markup=main_menu_keyboard()

        )
    else:
        await update.message.reply_html(
            rf"""Привет, {user.mention_html()}! Я бот для подготовки к егэ!""", reply_markup=main_menu_keyboard()
        )
        await db_table_val(user_id=int(us_id), user_name=us_name,
                           user_surname=us_sname, username=username, global_score=0)


async def db_table_val(user_id: int, user_name: str, user_surname: str, username: str, global_score):
    cursor.execute("""INSERT INTO user_data (user_id, user_name, user_surname, username, global_score)
                    VALUES (?, ?, ?, ?, ?)""",
                   (user_id, user_name, user_surname, username, global_score))
    conn.commit()


def main_menu_keyboard():
    main_reply_keyboard = [['Ударения', 'Пунктуация', 'Орфография'], ['Список лидеров'], ['Доп. Информация']]
    markup = ReplyKeyboardMarkup(main_reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    return markup


def menu_of_grammar():
    keyboard_of_grammar = [['Задание 9'],
                           ['Задание 10'],
                           ['Задание 11'],
                           ['Задание 12'],
                           ['Задание 15'],
                           ['в главное меню']]
    markup = ReplyKeyboardMarkup(keyboard_of_grammar, one_time_keyboard=False, resize_keyboard=True)
    return markup


def menu_of_punctuation():
    keyboard_of_grammar = [['Задание 16'],
                           ['Задание 17'],
                           ['Задание 18'],
                           ['Задание 19'],
                           ['Задание 20'],
                           ['Задание 21'],
                           ['в главное меню']]
    markup = ReplyKeyboardMarkup(keyboard_of_grammar, one_time_keyboard=False, resize_keyboard=True)
    return markup


async def message_about_new_record(user):
    user_id = str(user.message.from_user.id)
    global_score = cursor.execute(f'SELECT global_score FROM user_data WHERE User_id = {user_id}').fetchall()[0][0]
    if USERS[user_id]['score'] > global_score:
        us = user.effective_user
        print('score', global_score + USERS[user_id]['score'])
        await user.message.reply_html(
            f"""{us.mention_html()}, у вас новый рекорд! 🎉 
На данный момент счет: {global_score + USERS[user_id]['score']}""")
        cursor.execute("""UPDATE user_data
                        SET global_score = ?
                        WHERE user_id = ?""",
                       (global_score + USERS[user_id]['score'], user_id))
        conn.commit()
    else:
        await user.message.reply_html(
            f"""Ваш счет: {USERS[user_id]['score']}
Ваш рекорд: {global_score}""")
    USERS[user_id]['score'] = 0


async def create_list_of_leaders(user):
    data_users = cursor.execute("""SELECT * FROM user_data ORDER BY global_score""").fetchall()
    list_of_leaders = ''
    counter = 1
    for item in data_users[::-1][:10]:
        user_id = item[1]
        name = item[2]
        score = item[5]
        click_user_name = item[4]
        if not click_user_name:
            list_of_leaders += f'{counter}) <a href="tg://user?id={user_id}">{name}</a> ----> ' \
                               f'{score} points\n'
        else:
            list_of_leaders += f'{counter}) @{click_user_name} ----> {score} points\n'
        counter += 1
    await user.message.reply_html(list_of_leaders, reply_markup=main_menu_keyboard())


BOT_TOKEN = '5926455945:AAFvNA2LPuOmL0EDw3HVJkOJ1H5mOaNgfas'


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == '__main__':
    main()
