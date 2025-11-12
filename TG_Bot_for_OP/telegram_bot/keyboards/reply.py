# Звичайні ReplyKeyboard
from telebot import types


def create_simple_keyboard(one_time_keyboard=True, buttons=None):
    """Створює клавіатуру з кнопок"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2,
                                         resize_keyboard=True,
                                         one_time_keyboard=one_time_keyboard)
    buttons_list = []
    for button in buttons:
        buttons_list.append(types.KeyboardButton(button))
    if buttons_list:
        keyboard.add(*buttons_list)
    return keyboard


def create_keyboard():
    """Створює головне меню"""
    keyboard = types.ReplyKeyboardMarkup(True, row_width=2)
    button1 = types.KeyboardButton("меню")
    button3 = types.KeyboardButton("купити")
    button4 = types.KeyboardButton("вимкнути")
    keyboard.add(button1, button3, button4)
    return keyboard


def create_order_confirmation_keyboard():
    """Створює клавіатуру для підтвердження замовлення"""
    keyboard = types.ReplyKeyboardMarkup(True, row_width=2)
    keyboard.add(types.KeyboardButton("Замовити"), types.KeyboardButton("Скасувати"))
    return keyboard


