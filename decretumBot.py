import telebot
from telebot import types
import os
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, date, timedelta
import time, threading, schedule


load_dotenv(".env")
bot = telebot.TeleBot(os.getenv('token2'))
users = defaultdict(dict)
keys = ['name', 'goal', 'period', 'interval', 'reward']
user = dict(zip(keys, [None]*len(keys)))
cur_user = None
weekdays_torus = {'Mon': 'Пн.', 'Tue': 'Вт.', 'Wed': 'Ср.', 'Thu': 'Чт.', 'Fri': 'Пт.', 'Sat': 'Сб.', 'Sun': 'Вс.'}
weekdays_toeng = {y: x for x, y in weekdays_torus.items()}
cur_msg = None


@bot.message_handler(func=lambda msg: msg.text is not None and '/start' in msg.text)
def send_welcome(msg):
    global cur_user
    cur_user = msg.from_user.id
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Да', callback_data='old'),
                 types.InlineKeyboardButton('Нет', callback_data='new'))
    keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
    greet = 'Бла...бла...бла\nМы знакомы?'
    bot.send_message(msg.chat.id, greet, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def query_processing(call):
    global user
    global cur_user
    if call.data == 'new':
        user = dict.fromkeys(user, None)
        nxt = bot.send_message(call.message.chat.id, 'Как звать?')
        bot.register_next_step_handler(nxt, get_name_ask_goal)
    elif call.data == 'old':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Да', callback_data='remind_yes'),
                     types.InlineKeyboardButton('Нет', callback_data='remind_no'))
        keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
        nxt = 'Напоминания потребуются?'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data == 'stop_bot':
        txt = 'По Щучьему веленью, по кодову хотенью обнуляю сессию...'
        default_statement(call.message, txt)
    elif call.data == 'goal':
        nxt = bot.send_message(call.message.chat.id, 'Запоминаю цель...')
        bot.register_next_step_handler(nxt, get_goal_ask_period)
    elif call.data == 'info':
        txt = 'Крепко держимся, кто стоит лучше сесть...\nЗа основу взята аббревиатура S.M.A.R.T.\n' + \
              'К.И.С.К.А.\nКачество для качественного описания цели\nИзмеримость для оценки цели\n' + \
              'Совместимость для определения исполнителей\nКонструктивность для определения имещихся ресурсов\n' + \
              'Административность для органичения времени выполнения и прочих административных характеристик\n\n' + \
              'Надеюсь доходчиво, а теперь запоминаю цель...'
        nxt = bot.send_message(call.message.chat.id, txt)
        bot.register_next_step_handler(nxt, get_goal_ask_period)
    elif call.data == '1' or call.data == '7' or call.data == '30' or call.data == '180' or call.data == '365':
        get_period(call.message, call)
    elif call.data == 'date':
        nxt = bot.send_message(call.message.chat.id, 'Ожидаю дату в нужном формате (пример: 28.01.2023)...')
        bot.register_next_step_handler(nxt, get_period, call)
    elif call.data == 'remind_yes' or call.data == 'remind_no' or call.data in weekdays_torus or call.data == 'interval_done':
        get_interval(call)
    elif call.data == 'reward_yes' or call.data == 'reward_no':
        get_reward(call)
    else:
        bot.send_message(call.message.chat.id, 'Что-то не так...')


def get_name_ask_goal(msg):
    global user
    user['name'] = msg.text
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Цель', callback_data='goal'),
                 types.InlineKeyboardButton('Инфо', callback_data='info'))
    nxt = 'Цель (К.И.С.К.А.)?'
    bot.send_message(msg.chat.id, nxt, reply_markup=keyboard)


def get_goal_ask_period(msg):
    global cur_user
    global user
    if cur_user == msg.from_user.id:
        user['goal'] = msg.text
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('1', callback_data='1'),
                     types.InlineKeyboardButton('7', callback_data='7'),
                     types.InlineKeyboardButton('30', callback_data='30'),
                     types.InlineKeyboardButton('180', callback_data='180'),
                     types.InlineKeyboardButton('365', callback_data='365'))
        keyboard.add(types.InlineKeyboardButton('Указать дату завершения (ДД.ММ.ГГГГ)', callback_data='date'))
        nxt = 'За сколько дней цель будет выполнена?'
        bot.send_message(msg.chat.id, nxt, reply_markup=keyboard)
    else:
        txt = 'Я запутался в пользователях.\nОбнуляю сессию...'
        default_statement(msg, txt)


def default_statement(msg, txt):
    global user
    global cur_user
    global cur_msg
    bot.send_message(msg.chat.id, txt + '\nДля новой попытки /start')
    user = dict(zip(keys, [None] * len(keys)))
    cur_user = None
    cur_msg = None


def get_period(msg, call):
    global user
    global cur_user
    if cur_user == call.from_user.id:
        try:
            if call.data == 'date':
                user['period'] = datetime.strptime(msg.text, '%d.%m.%Y').date()
            else:
                user['period'] = date.today() + timedelta(days=int(call.data))
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Да', callback_data='remind_yes'),
                         types.InlineKeyboardButton('Нет', callback_data='remind_no'))
            keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
            nxt = 'Напоминания потребуются?'
            bot.send_message(msg.chat.id, nxt, reply_markup=keyboard)
        except BaseException as exception:
            # print(call.message.text)
            # print(call.data)
            # print('Ошибка: {}\nОписание: {}'.format(type(exception).__name__, exception))
            txt = 'Плохо у меня с датами, совсем плохо...придется обнуляться.'
            default_statement(call.message, txt)
    else:
        txt = 'Я запутался в пользователях.\nОбнуляю сессию...'
        default_statement(call.message, txt)


def get_interval(call):
    global user
    global cur_user
    global cur_msg
    if cur_user != call.from_user.id:
        return default_statement(call.message, 'Я запутался в пользователях.\nОбнуляю сессию...')
    if call.data == 'remind_no':
        txt = 'Движение к цели без напоминаний.'
        nxt = bot.send_message(call.message.chat.id, txt)
        bot.register_next_step_handler(nxt, get_reward)
    elif call.data == 'interval_done':
        if cur_msg is None:
            txt = 'Осталось выбрать время для напоминания в выбранные дни.\nОжидаю время напоминания в формате ЧЧ:ММ (пример: 7:00)...'
            nxt = bot.send_message(call.message.chat.id, txt)
            bot.register_next_step_handler(nxt, get_smth, call)
        else:
            try:
                user['interval'].add(datetime.strptime(cur_msg.text, '%H:%M').time())
                cur_msg = None
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton('Да', callback_data='reward_yes'),
                             types.InlineKeyboardButton('Нет', callback_data='reward_no'))
                keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
                nxt = 'Награда победителю (в случае наличия напоминаний, награждение происходит при напоминании)?'
                bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
            except BaseException as exception:
                # print('Ошибка: {}\nОписание: {}'.format(type(exception).__name__, exception))
                txt = 'Эпик фейл с обработкой времени...придется обнуляться.'
                default_statement(call.message, txt)
    elif call.data == 'remind_yes':
        user['interval'] = set()
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Пн.', callback_data='Mon'),
                     types.InlineKeyboardButton('Вт.', callback_data='Tue'),
                     types.InlineKeyboardButton('Ср.', callback_data='Wed'),
                     types.InlineKeyboardButton('Чт.', callback_data='Thu'),
                     types.InlineKeyboardButton('Пт.', callback_data='Fri'),
                     types.InlineKeyboardButton('Cб.', callback_data='Sat'),
                     types.InlineKeyboardButton('Вс.', callback_data='Sun'))
        keyboard.add(types.InlineKeyboardButton('Закончить выбор дней.', callback_data='interval_done'))
        nxt = 'Напоминания не настроены.\nВыберите дни для напоминания.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data in weekdays_torus:
        user['interval'].add(weekdays_torus[call.data])
        # keyboard = types.InlineKeyboardMarkup()
        # keyboard.add(types.InlineKeyboardButton('Пн.', callback_data='Mon'),
        #              types.InlineKeyboardButton('Вт.', callback_data='Tue'),
        #              types.InlineKeyboardButton('Ср.', callback_data='Wed'),
        #              types.InlineKeyboardButton('Чт.', callback_data='Thu'),
        #              types.InlineKeyboardButton('Пт.', callback_data='Fri'),
        #              types.InlineKeyboardButton('Cб.', callback_data='Sat'),
        #              types.InlineKeyboardButton('Вс.', callback_data='Sun'))
        # keyboard.add(types.InlineKeyboardButton('Закончить выбор дней.', callback_data='interval_done'))
        # nxt = 'Выбран(-ы) ' + ' '.join(user['interval']) + ' для напоминаний.\nМожно продолжить выбирать или закончить.'
        # bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
        bot.send_message(call.message.chat.id, 'Выбор пал на ' + weekdays_torus[call.data])
    else:
        txt = 'Я не смог принять интервал для напоминания, но можно попробовать еще.\nОбнуляю сессию...'
        default_statement(call.message, txt)


def get_smth(msg, call):
    global cur_msg
    cur_msg = msg
    if call.data == 'interval_done':
        get_interval(call)
    elif call.data == 'reward_yes':
        get_reward(call)
    else:
        print(cur_msg)
        txt = 'Нет счастье в ветвлении ветвления...\nОбнуляю сессию...'
        default_statement(call.message, txt)


def get_reward(call):
    global cur_msg
    if call.data == 'reward_no':
        gaining_goal(call)
    else:
        if cur_msg is None:
            nxt = bot.send_message(call.message.chat.id, 'Запоминаю награду...')
            bot.register_next_step_handler(nxt, get_smth, call)
        else:
            user['reward'] = cur_msg.text
            cur_msg = None
            gaining_goal(call)


def gaining_goal(call):
    global users
    global cur_user
    global user
    if cur_user == call.from_user.id:
        users[cur_user] = user
        print(users)
        txt = 'Записана необходимая информация для достижения цели. Это промежуточный результат и работа будетт продолжена...'
        default_statement(call.message, txt)
    else:
        txt = 'Я запутался в пользователях.\nОбнуляю сессию...'
        default_statement(call.message, txt)


def beep(chat_id) -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text='Beep!')


@bot.message_handler(commands=['set'])
def set_timer(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')


@bot.message_handler(commands=['unset'])
def unset_timer(message):
    schedule.clear(message.chat.id)


if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(1)
