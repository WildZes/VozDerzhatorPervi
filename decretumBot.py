import telebot
from telebot import types
import os
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime, date, timedelta
import time, threading, schedule
import tables as t


load_dotenv(".env")
bot = telebot.TeleBot(os.getenv('token2'))
users = defaultdict(dict)
keys = ['name', 'goal', 'period', 'interval', 'reward']
user = dict(zip(keys, [None]*len(keys)))
cur_user = None
weekdays_torus = {'Mon': 'Пн.', 'Tue': 'Вт.', 'Wed': 'Ср.', 'Thu': 'Чт.', 'Fri': 'Пт.', 'Sat': 'Сб.', 'Sun': 'Вс.'}
weekdays_toeng = {y: x for x, y in weekdays_torus.items()}
time_check = '00:0000:3001:0001:3002:0002:3003:0003:3004:0004:3005:0005:3006:0006:3007:0007:3008:0008:3009:0009:30' \
             '10:0010:3011:0011:3012:0012:3013:0013:3014:0014:3015:0015:3016:0016:3017:0017:3018:0018:3019:0019:30' \
             '20:0020:3021:0021:3022:0022:3023:0023:30'
cur_msg = None
inteval = []

@bot.message_handler(func=lambda msg: msg.text is not None and '/start' in msg.text)
def send_welcome(msg):
    global cur_user
    cur_user = msg.from_user.id
    keyboard = t.yes_no('Закончить.', 'old', 'new', 'stop_bot')
    # keyboard.add(types.InlineKeyboardButton('Да', callback_data='old'),
    #              types.InlineKeyboardButton('Нет', callback_data='new'))
    # keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
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
        #Implemented as forcing question about reminder to ease bot debugging
        keyboard = t.yes_no('Только начали, а мне уже скучно....', 'remind_yes', 'remind_no', 'stop_bot')
        # keyboard.add(types.InlineKeyboardButton('Да', callback_data='remind_yes'),
        #              types.InlineKeyboardButton('Нет', callback_data='remind_no'))
        # keyboard.add(types.InlineKeyboardButton('Пора остановиться', callback_data='stop_bot'))
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
    elif (call.data == 'remind_yes' or call.data == 'remind_no' or call.data in weekdays_torus or
          call.data == 'interval_done' or call.data in time_check):
        get_interval(call)
    elif call.data == 'reward_yes' or call.data == 'reward_no':
        get_reward(call)
    else:
        bot.send_message(call.message.chat.id, 'Что-то не так...Я не знаю что делать...')


def get_name_ask_goal(msg):
    global user
    user['name'] = msg.text
    keyboard = t.dual_choice('Цель', 'Инфо', 'goal', 'info')
    nxt = 'Цель (К.И.С.К.А.)?'
    bot.send_message(msg.chat.id, nxt, reply_markup=keyboard)


def get_goal_ask_period(msg):
    global cur_user
    global user
    if cur_user == msg.from_user.id:
        user['goal'] = msg.text
        keyboard = t.period()
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
            keyboard = t.yes_no('Пора остановиться.', 'remind_yes', 'remind_no', 'stop_bot')
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
    global interval
    if cur_user != call.from_user.id:
        return default_statement(call.message, 'Я запутался в пользователях.\nОбнуляю сессию...')
    if call.data == 'remind_no':
        txt = 'Движение к цели без напоминаний.'
        keyboard = t.yes_no('Все...в конец запутался....тормози!', 'reward_yes', 'reward_no', 'stop_bot')
        bot.send_message(call.message.chat.id, txt, reply_markup=keyboard)
    elif call.data == 'interval_done':
        keyboard = t.yes_no('Слишком долго, пожно прекратить...', 'reward_yes', 'reward_no', 'stop_bot')
        nxt = 'Награда победителю (в случае наличия напоминаний, награждение происходит при напоминании)?'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data == 'remind_yes':
        interval = []
        user['interval'] = set()
        keyboard = t.weekdays()
        nxt = 'Настройка напоминания.\nВыберите дни для напоминания.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data in weekdays_torus:
        interval.append(weekdays_torus[call.data])
        print(interval)
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.times()
        nxt = 'Настройка напоминания.\nВыберите время для напоминания (' + weekdays_torus[call.data] + ')'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data in time_check:
        print(interval)
        interval.append(call.data)
        if len(interval) == 2:
            user['interval'].add(tuple(interval))
            interval = []
        print(interval)
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.weekdays()
        nxt = 'Настройка напоминания.\nВыберите дни для напоминания.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
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
    txt = ''
    if cur_user == call.from_user.id:
        users[cur_user] = user
        print(users)
        if users[cur_user]['interval']:
            for i, v in enumerate(users[cur_user]['interval']):
                print(v[0], v[1])
                if v[0] == 'Пн.':
                    schedule.every().monday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Вт.':
                    schedule.every().tuesday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Ср.':
                    schedule.every().wednesday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Чт.':
                    schedule.every().thursday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Пт.':
                    schedule.every().friday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Сб.':
                    schedule.every().saturday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
                if v[0] == 'Вс.':
                    schedule.every().sunday.at(v[1]).do(beep, call.message.chat.id).tag(call.message.chat.id)
                    txt += f'Напоминание {i+1}: {v[0]} {v[1]}\n'
            print(schedule.get_jobs())
        else:
            txt = 'Записана необходимая информация для достижения цели. Это промежуточный результат и работа будетт продолжена...'
        default_statement(call.message, txt)
    else:
        txt = 'Я запутался в пользователях.\nОбнуляю сессию...'
        default_statement(call.message, txt)


def beep(chat_id, txt='Beep!') -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text=txt)


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
        time.sleep(0.5)
