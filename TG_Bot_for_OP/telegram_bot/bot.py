# Головний файл запуску бота
import telebot
from config import TOKEN
from .handlers import (
    register_start_handlers,
    register_message_handlers,
    register_callback_handlers
)

# Ініціалізація бота
bot = telebot.TeleBot(TOKEN)


def main():
    """Головна функція для запуску бота"""
    # Реєстрація всіх обробників
    register_start_handlers(bot)
    register_message_handlers(bot)
    register_callback_handlers(bot)
    
    print("Бот запущено...")
    bot.polling()


if __name__ == '__main__':
    main()

