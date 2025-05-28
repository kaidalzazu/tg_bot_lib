# handlers/book_handlers.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# --- Импорт меню ---
try:
    from config import MAIN_MENU
except ImportError:
    logger.critical("❌ Не найден файл config.py")
    raise


# --- Список доступных книг ---
async def list_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = None
    try:
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("SELECT id, title, author, year, inventory_number FROM books WHERE quantity > 0")
        rows = cur.fetchall()
        msg = "📚 Доступные книги:\n"
        for row in rows:
            msg += f"ID: {row[0]} — {row[1]} ({row[2]}, {row[3]}, №{row[4]})\n"
        await update.message.reply_text(msg or "Книг нет в наличии.", reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Ошибка загрузки книг: {e}")
        await update.message.reply_text("❌ Ошибка загрузки книг.")
    finally:
        if conn:
            conn.close()