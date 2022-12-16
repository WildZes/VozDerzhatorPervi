import pickle
import telebot
import os
from dotenv import load_dotenv
from collections import defaultdict
import time, threading, schedule
import tables as t


load_dotenv(".env")
bot = telebot.TeleBot(os.getenv('token3'))
users = defaultdict(dict)
keys = ['name', 'interval']
cur_user = None
weekdays_torus = {'Mon': 'Пн.', 'Tue': 'Вт.', 'Wed': 'Ср.', 'Thu': 'Чт.', 'Fri': 'Пт.', 'Sat': 'Сб.', 'Sun': 'Вс.'}
weekdays_toeng = {y: x for x, y in weekdays_torus.items()}
weekdays_coeff = {'Пн.': 1, 'Вт.': 2, 'Ср.': 3, 'Чт.': 4, 'Пт.': 5, 'Сб.': 6, 'Вс.': 7}
time_check = '00:0000:3001:0001:3002:0002:3003:0003:3004:0004:3005:0005:3006:0006:3007:0007:3008:0008:3009:0009:30' \
             '10:0010:3011:0011:3012:0012:3013:0013:3014:0014:3015:0015:3016:0016:3017:0017:3018:0018:3019:0019:30' \
             '20:0020:3021:0021:3022:0022:3023:0023:30'
cur_msg = None
interval = []

@bot.message_handler(func=lambda msg: msg.text is not None and '/start' in msg.text)
def send_welcome(msg):
    global cur_user
    global users
    cur_user = msg.from_user.id
    try:
        with open('telebot_data.pkl', 'rb') as f:
            users = pickle.load(f)
    except:
        print('No data file.')
    keyboard = t.yes_no('Закончить.', 'old', 'new', 'stop_bot')
    greet = 'Привет, я Декректум, бот\-напоминатель\. Создан для достижения одной важной цели, но был выпущен на волю для ' \
            'отправки напоминаний всем желающим\. Сейчас я умею запоминать текст напоминания отправлять этот текст в ' \
            'установленное время и создавать неограниченное количество напоминаний\.\nДополнительную информацию можно ' \
            'найти на [канале](https://t.me/zhiznKrasa)\n\nТеперь к делу\. Мы знакомы?'
    bot.send_message(msg.chat.id, greet, reply_markup=keyboard, parse_mode='MarkdownV2', disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: True)
def query_processing(call):
    global cur_user
    global users
    global interval
    if call.data == 'new' or call.data == 'name' or call.data == 'goal':
        if not users[cur_user] and call.data == 'new':
            nxt = bot.send_message(call.message.chat.id, 'Как звать?')
            bot.register_next_step_handler(nxt, get_name_ask_goal, call)
        elif users[cur_user]['name'] and call.data == 'new':
            bot.delete_message(call.message.chat.id, call.message.id)
            keyboard = t.yes_no('Закончить.', 'old', 'new', 'stop_bot')
            nxt = f'Обнаружил в базе пользователя с именем {users[cur_user]["name"]}.\nМожно продолжить давить "Нет", но ' \
                  f'это не будет весело...потому что беседа будет замкнута...'
            bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
        elif call.data == 'new' or call.data == 'name':
            nxt = bot.send_message(call.message.chat.id, 'Как звать?')
            bot.register_next_step_handler(nxt, get_name_ask_goal, call)
        else:
            nxt = bot.send_message(call.message.chat.id, 'Предлагаю ввести напоминание.')
            bot.register_next_step_handler(nxt, get_smth, call)
    elif call.data == 'old':
        if call.from_user.id not in users:
            bot.delete_message(call.message.chat.id, call.message.id)
            keyboard = t.yes_no('Закончить.', 'old', 'new', 'stop_bot')
            nxt = 'Данных пользователя нет в базе.\nНадо знакомиться и давить "Нет"...'
            bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
        else:
            if not users[cur_user]['interval']:
                users[cur_user]['interval'] = set()
            bot.delete_message(call.message.chat.id, call.message.id)
            keyboard = t.remind_changes(users, cur_user, weekdays_coeff)
            nxt = f'Инструкция:\nИмя/Стереть - заменить или стереть имя.\nНажатие любой кнопки с напоминанием, удалит ' \
                  f'это напоминание.\nСтереть ВСЕ - удалит все о пользователе {users[cur_user]["name"]}.'
            bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data == 'stop_bot':
        txt = 'По Щучьему веленью, по кодову хотенью обнуляю сессию...'
        default_statement(call.message, txt)
    elif (call.data == 'remind_yes' or call.data == 'remind_no' or call.data in weekdays_torus or
          call.data == 'interval_done' or call.data in time_check):
        get_interval(call)
    elif call.data == 'remind_next':
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.weekdays()
        nxt = f'Настройка напоминания "{interval[0]}".\nНужно выбрать день.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data == 'delete_user':
        gaining_goal(call)
    elif call.data in [f'remind,{x[3]}' for x in users[cur_user]['interval']]:
        interval = []
        for destroy in users[cur_user]['interval']:
            if f'remind,{destroy[3]}' != call.data:
                interval.append(destroy)
        if len(interval) != 0:
            users[cur_user]['interval'] = set(interval)
        else:
            users[cur_user]['interval'] = set()
        gaining_goal(call)
    elif call.data in [f'goal,{i}' for i, _ in enumerate(sorted(set(users[cur_user]['interval'])))]:
        remind = call.data.split(',')[1]
        interval_list = set([x[0] for x in users[cur_user]['interval']])
        remind = [x for i, x in enumerate(sorted(interval_list)) if str(i) == remind][0]
        interval = [remind]
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.weekdays()
        nxt = f'Настройка напоминания "{remind}".\nНужно выбрать день.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data == 'del_name':
        call.message.text = 'Имя удалено пользователем'
        get_name_ask_goal(call.message, call)
    else:
        bot.send_message(call.message.chat.id, 'Что-то не так...Я не знаю что делать...')


def get_smth(msg, call):
    global cur_msg
    global interval
    if msg.text == '/start':
        return send_welcome(msg)
    cur_msg = msg
    if call.data == 'new' or call.data == 'goal':
        call.data = 'remind_yes'
        get_interval(call)
    else:
        nxt = 'Нет счастья в ветвлении ветвления...\nОбнуляю сессию...'
        default_statement(call.message, nxt)


def get_name_ask_goal(msg, call):
    global users
    print(users)
    if users[cur_user]:
        users[cur_user]['name'] = msg.text
        keyboard = t.yes_no('Не сохранять.', 'old', 'interval_done', 'stop_bot')
        nxt = 'Еще замены будут?'
        bot.send_message(msg.chat.id, nxt, reply_markup=keyboard)
    elif msg.text == '/start':
        return send_welcome(msg)
    else:
        users[cur_user] = dict(zip(keys, [None] * len(keys)))
        users[cur_user]['name'] = msg.text
        if not users[cur_user]['interval']:
            users[cur_user]['interval'] = set()
        nxt = bot.send_message(msg.chat.id, 'Ввод напоминания. Я жду...')
        bot.register_next_step_handler(nxt, get_smth, call)


def get_interval(call):
    global cur_user
    global cur_msg
    global interval
    if cur_user != call.from_user.id:
        return default_statement(call.message, 'Я запутался в пользователях.\nОбнуляю сессию...')
    if call.data == 'remind_no':
        if users[cur_user]:
            users[cur_user]['interval'] = set()
            keyboard = t.yes_no('Стоп интервальные и любые изменения...', 'old', 'reward_no', 'stop_bot')
            nxt = 'Еще замены будут?'
            bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
        else:
            txt = 'Движение к цели без напоминаний.'
            keyboard = t.yes_no('Все...в конец запутался....тормози!', 'reward_yes', 'reward_no', 'stop_bot')
            bot.send_message(call.message.chat.id, txt, reply_markup=keyboard)
    elif call.data == 'interval_done':
        gaining_goal(call)
    elif call.data == 'remind_yes':
        interval = [cur_msg.text]
        cur_msg = None
        keyboard = t.weekdays()
        nxt = f'Настройка напоминания "{interval[0]}".\nНужно выбрать день.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data in weekdays_torus:
        interval.append(weekdays_torus[call.data])
        print(interval)
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.times()
        nxt = f'Настройка напоминания "{interval[0]}".\nНужно выбрать время.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    elif call.data in time_check:
        interval.append(call.data)
        if len(interval) == 3:
            interval.append(str(len(users[cur_user]['interval'])))
            users[cur_user]['interval'].add(tuple(interval))
            interval = [interval[0]]
        bot.delete_message(call.message.chat.id, call.message.id)
        keyboard = t.yes_no('Старт', 'goal', 'remind_next', 'interval_done')
        nxt = f'Нужно жмакнуть:\nДа - закончить c "{interval[0]}" и ввести другое.\nНет - продолжить ' \
              f'c "{interval[0]}".\nСтарт - завершить настройку и запустить отсчет.'
        bot.send_message(call.message.chat.id, nxt, reply_markup=keyboard)
    else:
        txt = 'Я не смог принять интервал для напоминания, но можно попробовать еще.\nОбнуляю сессию...'
        default_statement(call.message, txt)


def default_statement(msg, txt):
    global cur_user
    global cur_msg
    global interval
    bot.send_message(msg.chat.id, txt + '\n\nДля продолжения /start')
    cur_user = None
    cur_msg = None
    interval = []


def gaining_goal(call):
    global users
    global cur_user
    bot.delete_message(call.message.chat.id, call.message.id)
    nxt = ''
    if cur_user == call.from_user.id:
        if call.data == 'delete_user':
            del users[cur_user]
            nxt = 'Все данные о пользователе удалены...'
        if not nxt:
            nxt = f'Сейчас в работе:\nИмя: {users[cur_user]["name"]}\n' \
                  f'Напоминания:'
            schedule.clear(call.message.chat.id)
            for i, v in enumerate(sorted(list(users[cur_user]['interval']), key=lambda tup: (weekdays_coeff[tup[1]], tup[2]))):
                print(i,v[0], v[1], v[2])
                if v[1] == 'Пн.':
                    schedule.every().monday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Вт.':
                    schedule.every().tuesday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Ср.':
                    schedule.every().wednesday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Чт.':
                    schedule.every().thursday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Пт.':
                    schedule.every().friday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Сб.':
                    schedule.every().saturday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
                if v[1] == 'Вс.':
                    schedule.every().sunday.at(v[2]).do(beep, call.message.chat.id, v[0]).tag(call.message.chat.id)
                    nxt += f'\n    {i+1}: {v[0]} - {v[1]} {v[2]}'
            print(schedule.get_jobs())
        print(users)
        with open('telebot_data.pkl', 'wb') as f:
            pickle.dump(users, f)
        default_statement(call.message, nxt)
    else:
        nxt = 'Я запутался в пользователях.\nОбнуляю сессию...'
        default_statement(call.message, nxt)


def beep(chat_id, txt='Beep!') -> None:
    """Send the beep message."""
    bot.send_message(chat_id, text=txt)


if __name__ == "__main__":
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    while True:
        schedule.run_pending()
        time.sleep(0.5)
