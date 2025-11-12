# FSM (стани користувача)

# Словник для зберігання стану користувачів
user_states = {}

# Словник для зберігання замовлень користувачів
user_orders = {}


def get_user_state(user_id):
    """Отримує поточний стан користувача"""
    return user_states.get(user_id)


def set_user_state(user_id, state):
    """Встановлює стан користувача"""
    user_states[user_id] = state


def clear_user_state(user_id):
    """Очищає стан користувача"""
    user_states[user_id] = None


def init_user_order(user_id):
    """Ініціалізує замовлення користувача"""
    if user_id not in user_orders:
        user_orders[user_id] = {'items': []}
    else:
        user_orders[user_id]['items'] = []


def get_user_order(user_id):
    """Отримує замовлення користувача"""
    return user_orders.get(user_id, {'items': []})


def clear_user_order(user_id):
    """Очищає замовлення користувача"""
    user_orders[user_id] = {'items': []}


