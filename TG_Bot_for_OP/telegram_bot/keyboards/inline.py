# InlineKeyboardMarkup
from telebot import types

# Тут можна додати функції для створення inline-кнопок
# Наприклад, для вибору товарів, категорій тощо

def create_inline_product_keyboard(products):
    """Створює inline-клавіатуру для вибору товарів"""
    keyboard = types.InlineKeyboardMarkup()
    # Приклад використання (можна розширити за потреби)
    for product in products:
        keyboard.add(types.InlineKeyboardButton(
            text=product,
            callback_data=f"product_{product}"
        ))
    return keyboard


