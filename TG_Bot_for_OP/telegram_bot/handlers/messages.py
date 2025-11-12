# Текстові повідомлення
from telebot import types
from ..keyboards import create_keyboard, create_simple_keyboard, create_order_confirmation_keyboard
from ..states import (
    get_user_state, set_user_state, clear_user_state,
    init_user_order, get_user_order, clear_user_order
)
from ..utils import (
    menu_reader, get_product_names, is_valid_phone,
    calculate_total, save_to_buffer, append_to_log, format_order_message
)
from ..config import ADMIN_CHAT_ID


def register_message_handlers(bot):
    """Реєструє обробники текстових повідомлень"""
    
    @bot.message_handler(func=lambda message: message.text.lower() == "меню")
    def show_menu(message):
        """Показує меню користувачу"""
        men = menu_reader()
        bot.send_message(message.chat.id,
                         text=men,
                         reply_markup=create_simple_keyboard(False, ["Назад"]))

    @bot.message_handler(func=lambda message: message.text.lower() == "купити")
    def buy_menu(message):
        """Починає процес оформлення замовлення"""
        user_id = message.from_user.id
        set_user_state(user_id, "selecting_products")
        init_user_order(user_id)

        products = get_product_names()
        products.append("Завершити замовлення")
        products.append("Назад")
        bot.send_message(message.chat.id,
                         text="Оберіть товари (можна вибрати кілька разів):",
                         reply_markup=create_simple_keyboard(False, products))

    @bot.message_handler(func=lambda message: message.text in get_product_names())
    def handle_product_selection(message):
        """Обробляє вибір товару користувачем"""
        user_id = message.from_user.id

        if get_user_state(user_id) == "selecting_products":
            product_name = message.text
            user_order = get_user_order(user_id)
            user_order['items'].append(product_name)

            cart_items = user_order['items']
            cart_text = "\n".join([f"  • {item}" for item in cart_items])

            products = get_product_names()
            products.append("Завершити замовлення")
            products.append("Назад")

            bot.send_message(message.chat.id,
                             text=f"✅ Додано: {product_name}\n\n🛒 У кошику:\n{cart_text}",
                             reply_markup=create_simple_keyboard(False, products))

    @bot.message_handler(func=lambda message: message.text.lower() == "завершити замовлення")
    def finish_order(message):
        """Завершує вибір товарів і починає збір даних користувача"""
        user_id = message.from_user.id
        user_order = get_user_order(user_id)

        if not user_order.get('items'):
            bot.send_message(message.chat.id,
                             text="❌ Ваш кошик порожній!",
                             reply_markup=create_keyboard())
            return

        set_user_state(user_id, "waiting_name")
        bot.send_message(message.chat.id,
                         text="📝 Введіть ваше ім'я:",
                         reply_markup=types.ReplyKeyboardRemove())

    @bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == "waiting_name")
    def get_name(message):
        """Отримує ім'я користувача"""
        user_id = message.from_user.id
        user_order = get_user_order(user_id)
        user_order['name'] = message.text
        set_user_state(user_id, "waiting_phone")
        bot.send_message(message.chat.id, 
                         "📞 Введіть ваш номер телефону:\n(Наприклад: +380501234567 або 050 123 45 67)")

    @bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == "waiting_phone")
    def get_phone(message):
        """Отримує номер телефону користувача з валідацією"""
        user_id = message.from_user.id
        phone = message.text

        # Перевіряємо, чи це дійсно номер телефону
        if is_valid_phone(phone):
            user_order = get_user_order(user_id)
            user_order['phone'] = phone
            set_user_state(user_id, "waiting_address")
            bot.send_message(message.chat.id, "📍 Введіть адресу доставки:")
        else:
            # Якщо введено текст замість номера
            bot.send_message(message.chat.id,
                             "❌ Помилка! Ви ввели текст, а не номер телефону.\n"
                             "Будь ласка, введіть коректний номер телефону:\n"
                             "(Наприклад: +380501234567 або 050 123 45 67)")
            # Стан залишається "waiting_phone", тому бот знову чекатиме на номер

    @bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == "waiting_address")
    def get_address(message):
        """Отримує адресу доставки і показує підсумок замовлення"""
        user_id = message.from_user.id
        user_order = get_user_order(user_id)
        user_order['address'] = message.text

        # Розраховуємо вартість
        subtotal, delivery, total = calculate_total(user_order['items'])
        user_order['subtotal'] = subtotal
        user_order['delivery'] = round(delivery, 2)
        user_order['total'] = round(total, 2)

        # Зберігаємо в буфер
        save_to_buffer(user_id, user_order)

        # Показуємо підсумок
        order_msg = format_order_message(user_order)

        set_user_state(user_id, "confirming_order")
        bot.send_message(message.chat.id,
                         text=f"{order_msg}\n\n✅ Підтвердіть замовлення:",
                         reply_markup=create_order_confirmation_keyboard())

    @bot.message_handler(func=lambda message: message.text.lower() == "замовити")
    def confirm_order(message):
        """Підтверджує замовлення і відправляє його адміну"""
        user_id = message.from_user.id

        if get_user_state(user_id) == "confirming_order":
            user_order = get_user_order(user_id)
            
            # Відправляємо адміну
            try:
                order_msg = format_order_message(user_order)
                bot.send_message(ADMIN_CHAT_ID, order_msg)
            except Exception as e:
                print(f"Помилка відправки адміну: {e}")

            # Додаємо в лог
            append_to_log()

            # Очищаємо стан
            clear_user_state(user_id)
            clear_user_order(user_id)

            bot.send_message(message.chat.id,
                             text="✅ Замовлення успішно оформлено! Очікуйте на дзвінок.",
                             reply_markup=create_keyboard())

    @bot.message_handler(func=lambda message: message.text.lower() == "скасувати")
    def cancel_order(message):
        """Скасовує замовлення"""
        user_id = message.from_user.id
        clear_user_state(user_id)
        clear_user_order(user_id)
        bot.send_message(message.chat.id,
                         text="❌ Замовлення скасовано",
                         reply_markup=create_keyboard())

    @bot.message_handler(func=lambda message: message.text.lower() == "назад")
    def go_back(message):
        """Повертає користувача в головне меню"""
        user_id = message.from_user.id
        clear_user_state(user_id)
        bot.send_message(message.chat.id,
                         text="Повернення у головне меню:",
                         reply_markup=create_keyboard())

    @bot.message_handler(func=lambda message: message.text.lower() == "вимкнути")
    def remove_keyboard(message):
        """Приховує клавіатуру"""
        remove_kb = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Кнопки закрито", reply_markup=remove_kb)
        bot.send_message(message.chat.id, "Хочете почати заново? /start")

