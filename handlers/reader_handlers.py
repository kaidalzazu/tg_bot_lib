from telegram import Update
from telegram.ext import ContextTypes
import sqlite3


async def register_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    cur.execute("SELECT id FROM readers WHERE telegram_id=?", (user.id,))
    if cur.fetchone():
        await update.message.reply_text(f"Добро пожаловать, {user.full_name}!", reply_markup=MAIN_MENU)
        conn.close()
        return True  # Уже зарегистрирован

    await update.message.reply_text("Введите ваше ФИО и группу через пробел.\nПример: Иван Иванов ИВТ-23")
    conn.close()
    return False  # Нужна регистрация