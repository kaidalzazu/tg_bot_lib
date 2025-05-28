# handlers/reader_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
import logging

logger = logging.getLogger(__name__)

async def register_reader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    conn = None
    try:
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("SELECT id FROM readers WHERE telegram_id=?", (user.id,))
        if cur.fetchone():
            return True  # Уже зарегистрирован
        return False  # Нужна регистрация
    finally:
        if conn:
            conn.close()
            # конец