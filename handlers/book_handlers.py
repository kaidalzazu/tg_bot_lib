# handlers/book_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) < 4:
        await update.message.reply_text("Использование: /add_book Название Автор Год Инвентарный_номер")
        return

    title = ' '.join(args[:-3])
    author = args[-3]
    year = int(args[-2])
    inv_num = args[-1]

    conn = None
    try:
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM books WHERE inventory_number=?", (inv_num,))
        if cur.fetchone():
            await update.message.reply_text("❌ Такой инвентарный номер уже существует.")
            return

        cur.execute("INSERT INTO books(title, author, year, inventory_number) VALUES(?,?,?,?)",
                    (title, author, year, inv_num))
        conn.commit()
        await update.message.reply_text(f"✅ Книга '{title}' добавлена.")
    except ValueError:
        await update.message.reply_text("❌ Год должен быть числом.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении книги: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        if conn:
            conn.close()


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
        await update.message.reply_text(msg or "Книг нет в наличии.")
    except Exception as e:
        logger.error(f"Ошибка загрузки книг: {e}")
        await update.message.reply_text("❌ Ошибка при загрузке списка книг.")
    finally:
        if conn:
            conn.close()