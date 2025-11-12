# Допоміжні функції
import re
from .config import MENU_FILE, LOG_FILE, BUFFER_LOG_FILE, DELIVERY_PERCENTAGE


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
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        return file.read()


def get_products_dict():
    """Повертає словник товарів {назва: ціна}"""
    products = {}
    with open(MENU_FILE, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            
            # Підтримка обох форматів: "назва = ціна" та "назва ціна"
            if "=" in line:
                # Формат з знаком "="
                parts = line.split("=", 1)
                name = parts[0].strip()
                price_str = parts[1].strip()
            else:
                # Формат без "=" - шукаємо останнє число в рядку
                import re
                match = re.search(r'(\d+)\s*$', line)
                if match:
                    price_str = match.group(1)
                    name = line[:match.start()].strip()
                else:
                    continue  # Пропускаємо рядок, якщо не знайдено ціну
            
            try:
                price = int(price_str)
                products[name] = price
            except ValueError:
                continue  # Пропускаємо рядок, якщо ціна не є числом
    return products


def get_product_names():
    """Повертає список назв товарів"""
    return list(get_products_dict().keys())


def calculate_total(items):
    """Розраховує загальну вартість з доставкою"""
    products = get_products_dict()
    subtotal = sum(products.get(item, 0) for item in items)
    delivery = subtotal * DELIVERY_PERCENTAGE
    total = subtotal + delivery
    return subtotal, delivery, total


def save_to_buffer(user_id, order_data):
    """Зберігає замовлення в Buffer log.txt (перезаписує)"""
    with open(BUFFER_LOG_FILE, "w", encoding="utf-8") as file:
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
    with open(BUFFER_LOG_FILE, "r", encoding="utf-8") as buffer:
        buffer_content = buffer.read()

    with open(LOG_FILE, "a", encoding="utf-8") as log:
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

