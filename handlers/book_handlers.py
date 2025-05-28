# handlers/book_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# --- Импортируем MAIN_MENU ---
try:
    from config import MAIN_MENU
except ImportError:
    logger.critical("❌ Не найден файл config.py")
    raise


# --- Функция добавления книги ---
async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if len(args) < 4:
        await update.message.reply_text("Использование: /add_book Название Автор Год Инвентарный_номер")
        return

    try:
        title = ' '.join(args[:-3])
        author = args[-3]
        year = int(args[-2])
        inv_num = args[-1]

        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        # Проверяем, есть ли книга с таким инвентарным номером
        cur.execute("SELECT * FROM books WHERE inventory_number=?", (inv_num,))
        if cur.fetchone():
            await update.message.reply_text("❌ Книга с таким инвентарным номером уже существует.")
            return

        # Добавляем новую книгу
        cur.execute("INSERT INTO books(title, author, year, inventory_number) VALUES(?,?,?,?)",
                    (title, author, year, inv_num))
        conn.commit()
        await update.message.reply_text(f"✅ Книга '{title}' добавлена.", reply_markup=MAIN_MENU)
    except ValueError:
        logger.error("❌ Год должен быть числом.")
        await update.message.reply_text("❌ Год должен быть числом.", reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Ошибка при добавлении книги: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}", reply_markup=MAIN_MENU)
    finally:
        conn.close()


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
        await update.message.reply_text("❌ Ошибка загрузки списка книг.")
    finally:
        if conn:
            conn.close()