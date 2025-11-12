# /start, /help тощо
from ..keyboards import create_keyboard
from ..states import clear_user_state, init_user_order


def register_start_handlers(bot):
    """Реєструє обробники команд /start та /help"""
    
    @bot.message_handler(commands=['start'])
    def start(message):
        """Обробник команди /start"""
        user_id = message.from_user.id
        clear_user_state(user_id)
        init_user_order(user_id)
        bot.send_message(message.chat.id,
                         text="Вітаємо! Оберіть дію:",
                         reply_markup=create_keyboard())

    @bot.message_handler(commands=['help'])
    def help_command(message):
        """Обробник команди /help"""
        help_text = (
            "📖 Довідка по боту:\n\n"
            "/start - Почати роботу з ботом\n"
            "/help - Показати цю довідку\n\n"
            "Основні команди:\n"
            "• меню - Переглянути меню\n"
            "• купити - Оформити замовлення\n"
            "• вимкнути - Приховати клавіатуру\n"
            "• назад - Повернутися в головне меню"
        )
        bot.send_message(message.chat.id, text=help_text)

