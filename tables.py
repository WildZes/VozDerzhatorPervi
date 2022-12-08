from telebot import types
from telebot.types import InlineKeyboardButton as Button

def yes_no(txt, cby, cbn, cbtxt):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Да', callback_data=cby),
                 types.InlineKeyboardButton('Нет', callback_data=cbn))
    keyboard.add(types.InlineKeyboardButton(txt, callback_data=cbtxt))
    return keyboard

def dual_choice(txt1, txt2, cb1, cb2):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(txt1, callback_data=cb1),
                 types.InlineKeyboardButton(txt2, callback_data=cb2))
    return keyboard

def period():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('1', callback_data='1'),
                 types.InlineKeyboardButton('7', callback_data='7'),
                 types.InlineKeyboardButton('30', callback_data='30'),
                 types.InlineKeyboardButton('180', callback_data='180'),
                 types.InlineKeyboardButton('365', callback_data='365'))
    keyboard.add(types.InlineKeyboardButton('Указать дату завершения (ДД.ММ.ГГГГ)', callback_data='date'))
    return keyboard

def weekdays():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Пн.', callback_data='Mon'),
                 types.InlineKeyboardButton('Вт.', callback_data='Tue'),
                 types.InlineKeyboardButton('Ср.', callback_data='Wed'),
                 types.InlineKeyboardButton('Чт.', callback_data='Thu'),
                 types.InlineKeyboardButton('Пт.', callback_data='Fri'),
                 types.InlineKeyboardButton('Cб.', callback_data='Sat'),
                 types.InlineKeyboardButton('Вс.', callback_data='Sun'))
    keyboard.add(types.InlineKeyboardButton('Закончить настройку.', callback_data='interval_done'))
    return keyboard

# def times():
#     keyboard = types.InlineKeyboardMarkup()
#     keyboard.add(types.InlineKeyboardButton('Пн.', callback_data='Mon'),
#                  types.InlineKeyboardButton('Вт.', callback_data='Tue'),
#                  types.InlineKeyboardButton('Ср.', callback_data='Wed'),
#                  types.InlineKeyboardButton('Чт.', callback_data='Thu'),
#                  types.InlineKeyboardButton('Пт.', callback_data='Fri'),
#                  types.InlineKeyboardButton('Cб.', callback_data='Sat'),
#                  types.InlineKeyboardButton('Вс.', callback_data='Sun'))
#     keyboard.add(types.InlineKeyboardButton('Закончить настройку.', callback_data='interval_done'))
#     return keyboard

def times(call=None): #Whanted to use call as chat follower, but maybe it is useless
    buttons = [
        [
            Button('00:00', callback_data='00:00'),
            Button('00:30', callback_data='00:30'),
            Button('01:00', callback_data='01:00'),
            Button('01:30', callback_data='01:30'),
            Button('02:00', callback_data='02:00'),
            Button('02:30', callback_data='02:30'),
        ],
        [
            Button('03:00', callback_data='03:00'),
            Button('03:30', callback_data='03:30'),
            Button('04:00', callback_data='04:00'),
            Button('04:30', callback_data='04:30'),
            Button('05:00', callback_data='05:00'),
            Button('05:30', callback_data='05:30'),
        ],
        [
            Button('06:00', callback_data='06:00'),
            Button('06:30', callback_data='06:30'),
            Button('07:00', callback_data='07:00'),
            Button('07:30', callback_data='07:30'),
            Button('08:00', callback_data='08:00'),
            Button('08:30', callback_data='08:30'),
        ],
        [
            Button('09:00', callback_data='09:00'),
            Button('09:30', callback_data='09:30'),
            Button('10:00', callback_data='10:00'),
            Button('10:30', callback_data='10:30'),
            Button('11:00', callback_data='11:00'),
            Button('11:30', callback_data='11:30'),
        ],
        [
            Button('12:00', callback_data='12:00'),
            Button('12:30', callback_data='12:30'),
            Button('13:00', callback_data='13:00'),
            Button('13:30', callback_data='13:30'),
            Button('14:00', callback_data='14:00'),
            Button('14:30', callback_data='14:30'),
        ],
        [
            Button('15:00', callback_data='15:00'),
            Button('15:30', callback_data='15:30'),
            Button('16:00', callback_data='16:00'),
            Button('16:30', callback_data='16:30'),
            Button('17:00', callback_data='17:00'),
            Button('17:30', callback_data='17:30'),
        ],
        [
            Button('18:00', callback_data='18:00'),
            Button('18:30', callback_data='18:30'),
            Button('19:00', callback_data='19:00'),
            Button('19:30', callback_data='19:30'),
            Button('20:00', callback_data='20:00'),
            Button('20:30', callback_data='20:30'),
        ],
        [
            Button('21:00', callback_data='21:00'),
            Button('21:30', callback_data='21:30'),
            Button('22:00', callback_data='22:00'),
            Button('22:30', callback_data='22:30'),
            Button('23:00', callback_data='23:00'),
            Button('23:30', callback_data='23:30'),
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(buttons)
    return keyboard
