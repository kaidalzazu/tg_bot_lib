# handlers/reader_handlers.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3
import logging

logger = logging.getLogger(__name__)

# --- Импорт меню ---
try:
    from config import MAIN_MENU
except ImportError:
    logger.critical("❌ Не найден файл config.py")
    raise


async def register_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = None
    try:
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM readers WHERE telegram_id=?", (user.id,))
        if cur.fetchone():
            await update.message.reply_text(f"Добро пожаловать, {user.full_name}!", reply_markup=MAIN_MENU)
            context.user_data.clear()
            return True
        else:
            await update.message.reply_text("Введите ваше ФИО и группу через пробел.\nПример: Иван Иванов ИВТ-23")
            context.user_data['state'] = "register"
            return False
    except Exception as e:
        logger.error(f"Ошибка регистрации: {e}")
        await update.message.reply_text("❌ Ошибка регистрации.")
        return False
    finally:
        if conn:
            conn.close()