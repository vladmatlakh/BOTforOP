# Конфігураційні змінні
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота з змінних оточення
TOKEN = os.getenv('TOKEN')

# ID адміністратора для отримання замовлень
ADMIN_CHAT_ID = int(os.getenv('ADMIN_ID'))

# Шлях до файлу меню
MENU_FILE = "Menu.txt"

# Шлях до файлу логів
LOG_FILE = "log.txt"

# Шлях до буферного файлу замовлень
BUFFER_LOG_FILE = "Buffer log.txt"

# Відсоток доставки (5%)
DELIVERY_PERCENTAGE = 0.05


