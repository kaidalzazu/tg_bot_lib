from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["📚 Доступные книги", "📖 Мои книги"],
     ["📦 Получить книгу", "⮿ Вернуть книгу"]],
    resize_keyboard=True
)

async def list_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, year, inventory_number FROM books WHERE quantity > 0")
    rows = cur.fetchall()
    msg = "📚 Доступные книги:\n"
    for row in rows:
        msg += f"ID: {row[0]} — {row[1]} ({row[2]}, {row[3]}, №{row[4]})\n"
    await update.message.reply_text(msg or "Книг нет в наличии.", reply_markup=MAIN_MENU)
    conn.close()