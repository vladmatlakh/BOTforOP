import telebot
import os
from dotenv import load_dotenv
from telebot import types
import re

load_dotenv()

bot = telebot.TeleBot(os.getenv('TOKEN'))

# ====== ВКАЖІТЬ ТУТ ВАШ TELEGRAM ID ======
ADMIN_CHAT_ID = int(os.getenv('ADMIN_ID'))  # <--- ЗАМІНІТЬ НА ВАШ TELEGRAM ID
# Щоб дізнатися свій ID, напишіть боту @userinfobot
# =========================================

# Словник для зберігання стану користувачів
user_states = {}
user_orders = {}


def is_valid_phone(phone):
    """
    Перевіряє, чи є введений текст номером телефону.
    Дозволяє формати: +380501234567, 0501234567, 050 123 45 67, 050-123-45-67 і т.д.
    """
    # Видаляємо всі пробіли, дефіси, дужки
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Перевіряємо, чи складається з цифр (можливо з + на початку)
    if cleaned_phone.startswith('+'):
        cleaned_phone = cleaned_phone[1:]

    # Перевіряємо, чи це тільки цифри та чи достатня довжина (мінімум 9 цифр)
    if cleaned_phone.isdigit() and len(cleaned_phone) >= 9:
        return True
    return False


def menu_reader():
    """Читає меню з файлу Menu.txt"""
    with open("Menu.txt", "r", encoding="utf-8") as file:
        return file.read()


def get_products_dict():
    """Повертає словник товарів {назва: ціна}"""
    products = {}
    with open("Menu.txt", "r", encoding="utf-8") as file:
        for line in file:
            if line.strip() and "=" in line:
                name = line.split("=")[0].strip()
                price = int(line.split("=")[1].strip())
                products[name] = price
    return products


def get_product_names():
    """Повертає список назв товарів"""
    return list(get_products_dict().keys())


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


def calculate_total(items):
    """Розраховує загальну вартість з доставкою"""
    products = get_products_dict()
    subtotal = sum(products.get(item, 0) for item in items)
    delivery = subtotal * 0.05
    total = subtotal + delivery
    return subtotal, delivery, total


def save_to_buffer(user_id, order_data):
    """Зберігає замовлення в Buffer log.txt (перезаписує)"""
    with open("Buffer log.txt", "w", encoding="utf-8") as file:
        file.write(f"User ID: {user_id}\n")
        file.write(f"Ім'я: {order_data['name']}\n")
        file.write(f"Телефон: {order_data['phone']}\n")
        file.write(f"Адреса: {order_data['address']}\n")
        file.write(f"\nТовари:\n")
        for item in order_data['items']:
            file.write(f"  - {item}\n")
        file.write(f"\nВартість товарів: {order_data['subtotal']} грн\n")
        file.write(f"Доставка (5%): {order_data['delivery']} грн\n")
        file.write(f"Всього до оплати: {order_data['total']} грн\n")


def append_to_log():
    """Додає замовлення з буфера в log.txt"""
    with open("Buffer log.txt", "r", encoding="utf-8") as buffer:
        buffer_content = buffer.read()

    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(buffer_content)
        log.write("\n" + "-" * 50 + "\n\n")


def format_order_message(order_data):
    """Форматує повідомлення про замовлення"""
    msg = "🛍️ НОВЕ ЗАМОВЛЕННЯ\n\n"
    msg += f"👤 Ім'я: {order_data['name']}\n"
    msg += f"📞 Телефон: {order_data['phone']}\n"
    msg += f"📍 Адреса: {order_data['address']}\n\n"
    msg += "🍽️ Товари:\n"
    for item in order_data['items']:
        msg += f"  • {item}\n"
    msg += f"\n💰 Вартість товарів: {order_data['subtotal']} грн\n"
    msg += f"🚚 Доставка (5%): {order_data['delivery']} грн\n"
    msg += f"💵 Всього до оплати: {order_data['total']} грн"
    return msg


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    user_orders[user_id] = {'items': []}
    bot.send_message(message.chat.id,
                     text="Вітаємо! Оберіть дію:",
                     reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text.lower() == "меню")
def show_menu(message):
    men = menu_reader()
    bot.send_message(message.chat.id,
                     text=men,
                     reply_markup=create_simple_keyboard(False, ["Назад"]))


@bot.message_handler(func=lambda message: message.text.lower() == "купити")
def buy_menu(message):
    user_id = message.from_user.id
    user_states[user_id] = "selecting_products"
    if user_id not in user_orders:
        user_orders[user_id] = {'items': []}
    else:
        user_orders[user_id]['items'] = []

    products = get_product_names()
    products.append("Завершити замовлення")
    products.append("Назад")
    bot.send_message(message.chat.id,
                     text="Оберіть товари (можна вибрати кілька разів):",
                     reply_markup=create_simple_keyboard(False, products))


@bot.message_handler(func=lambda message: message.text in get_product_names())
def handle_product_selection(message):
    user_id = message.from_user.id

    if user_states.get(user_id) == "selecting_products":
        product_name = message.text
        user_orders[user_id]['items'].append(product_name)

        cart_items = user_orders[user_id]['items']
        cart_text = "\n".join([f"  • {item}" for item in cart_items])

        products = get_product_names()
        products.append("Завершити замовлення")
        products.append("Назад")

        bot.send_message(message.chat.id,
                         text=f"✅ Додано: {product_name}\n\n🛒 У кошику:\n{cart_text}",
                         reply_markup=create_simple_keyboard(False, products))


@bot.message_handler(func=lambda message: message.text.lower() == "завершити замовлення")
def finish_order(message):
    user_id = message.from_user.id

    if not user_orders.get(user_id, {}).get('items'):
        bot.send_message(message.chat.id,
                         text="❌ Ваш кошик порожній!",
                         reply_markup=create_keyboard())
        return

    user_states[user_id] = "waiting_name"
    bot.send_message(message.chat.id,
                     text="📝 Введіть ваше ім'я:",
                     reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_name")
def get_name(message):
    user_id = message.from_user.id
    user_orders[user_id]['name'] = message.text
    user_states[user_id] = "waiting_phone"
    bot.send_message(message.chat.id, "📞 Введіть ваш номер телефону:\n(Наприклад: +380501234567 або 050 123 45 67)")


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_phone")
def get_phone(message):
    user_id = message.from_user.id
    phone = message.text

    # Перевіряємо, чи це дійсно номер телефону
    if is_valid_phone(phone):
        user_orders[user_id]['phone'] = phone
        user_states[user_id] = "waiting_address"
        bot.send_message(message.chat.id, "📍 Введіть адресу доставки:")
    else:
        # Якщо введено текст замість номера
        bot.send_message(message.chat.id,
                         "❌ Помилка! Ви ввели текст, а не номер телефону.\n"
                         "Будь ласка, введіть коректний номер телефону:\n"
                         "(Наприклад: +380501234567 або 050 123 45 67)")
        # Стан залишається "waiting_phone", тому бот знову чекатиме на номер


@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "waiting_address")
def get_address(message):
    user_id = message.from_user.id
    user_orders[user_id]['address'] = message.text

    # Розраховуємо вартість
    subtotal, delivery, total = calculate_total(user_orders[user_id]['items'])
    user_orders[user_id]['subtotal'] = subtotal
    user_orders[user_id]['delivery'] = round(delivery, 2)
    user_orders[user_id]['total'] = round(total, 2)

    # Зберігаємо в буфер
    save_to_buffer(user_id, user_orders[user_id])

    # Показуємо підсумок
    order_msg = format_order_message(user_orders[user_id])

    keyboard = types.ReplyKeyboardMarkup(True, row_width=2)
    keyboard.add(types.KeyboardButton("Замовити"), types.KeyboardButton("Скасувати"))

    user_states[user_id] = "confirming_order"
    bot.send_message(message.chat.id,
                     text=f"{order_msg}\n\n✅ Підтвердіть замовлення:",
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text.lower() == "замовити")
def confirm_order(message):
    user_id = message.from_user.id

    if user_states.get(user_id) == "confirming_order":
        # Відправляємо адміну
        try:
            order_msg = format_order_message(user_orders[user_id])
            bot.send_message(ADMIN_CHAT_ID, order_msg)
        except Exception as e:
            print(f"Помилка відправки адміну: {e}")

        # Додаємо в лог
        append_to_log()

        # Очищаємо стан
        user_states[user_id] = None
        user_orders[user_id] = {'items': []}

        bot.send_message(message.chat.id,
                         text="✅ Замовлення успішно оформлено! Очікуйте на дзвінок.",
                         reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text.lower() == "скасувати")
def cancel_order(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    user_orders[user_id] = {'items': []}
    bot.send_message(message.chat.id,
                     text="❌ Замовлення скасовано",
                     reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text.lower() == "назад")
def go_back(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    bot.send_message(message.chat.id,
                     text="Повернення у головне меню:",
                     reply_markup=create_keyboard())


@bot.message_handler(func=lambda message: message.text.lower() == "вимкнути")
def remove_keyboard(message):
    remove_kb = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Кнопки закрито", reply_markup=remove_kb)
    bot.send_message(message.chat.id, "Хочете почати заново? /start")


if __name__ == '__main__':
    print("Бот запущено...")
    bot.polling()