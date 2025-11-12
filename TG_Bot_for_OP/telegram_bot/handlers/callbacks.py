# Inline-кнопки (callback-и)

def register_callback_handlers(bot):
    """Реєструє обробники callback-запитів від inline-кнопок"""
    
    # Приклад обробника callback (можна розширити за потреби)
    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        """Базовий обробник для всіх callback-запитів"""
        # Тут можна додати логіку обробки різних callback_data
        # Наприклад:
        # if call.data.startswith("product_"):
        #     product_name = call.data.replace("product_", "")
        #     # Обробка вибору товару
        #     bot.answer_callback_query(call.id, f"Вибрано: {product_name}")
        pass


