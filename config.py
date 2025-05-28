# config.py

from telegram import ReplyKeyboardMarkup

# --- Главное меню ---
MAIN_MENU = ReplyKeyboardMarkup(
    [["📚 Доступные книги", "📖 Мои книги"],
     ["📦 Получить книгу", "⮿ Вернуть книгу"]],
    resize_keyboard=True
)

# --- Состояния ---
STATE_AWAITING_ISSUE = "issue"
STATE_AWAITING_RETURN = "return"