# handlers/loan_handlers.py

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import sqlite3
import logging

logger = logging.getLogger(__name__)

async def my_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conn = None
    try:
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()
        cur.execute("""SELECT l.id, b.title, l.issue_date 
                       FROM loans l
                       JOIN books b ON l.book_id = b.id
                       WHERE l.reader_id = (SELECT id FROM readers WHERE telegram_id = ?) AND l.return_date IS NULL""",
                    (user_id,))
        rows = cur.fetchall()
        msg = "📖 Ваши книги:\n"
        for row in rows:
            msg += f"Выдача #{row[0]} — {row[1]} (выдана {row[2]})\n"
        await update.message.reply_text(msg or "У вас пока нет книг.")
    except Exception as e:
        logger.error(f"Ошибка при получении книг: {e}")
        await update.message.reply_text("❌ Ошибка загрузки данных.")
    finally:
        if conn:
            conn.close()


async def issue_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID книги для выдачи:")
        return

    try:
        book_id = int(args[0])
        telegram_id = update.effective_user.id
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
        qty_row = cur.fetchone()
        if not qty_row or qty_row[0] <= 0:
            await update.message.reply_text("❌ Эта книга недоступна.")
            return

        cur.execute("SELECT id FROM readers WHERE telegram_id=?", (telegram_id,))
        reader_row = cur.fetchone()
        if not reader_row:
            await update.message.reply_text("❌ Сначала зарегистрируйтесь через /start")
            return

        reader_id = reader_row[0]
        today = datetime.now().strftime("%Y-%m-%d")

        cur.execute("INSERT INTO loans(book_id, reader_id, issue_date) VALUES(?,?,?)",
                    (book_id, reader_id, today))
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id=?", (book_id,))
        conn.commit()
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        await update.message.reply_text(f"✅ Книга {book_id} выдана до {due}.")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID книги.")
    except Exception as e:
        logger.error(f"Ошибка выдачи: {e}")
        await update.message.reply_text(f"❌ Ошибка выдачи: {e}")
    finally:
        conn.close()


async def return_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID выдачи для возврата:")
        return

    try:
        loan_id = int(args[0])
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        cur.execute("SELECT book_id FROM loans WHERE id=? AND return_date IS NULL", (loan_id,))
        res = cur.fetchone()
        if not res:
            await update.message.reply_text("❌ Не найдено активной выдачи с таким ID.")
            return

        book_id = res[0]
        today = datetime.now().strftime("%Y-%m-%d")

        cur.execute("UPDATE loans SET return_date = ? WHERE id = ?", (today, loan_id))
        cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
        conn.commit()
        await update.message.reply_text(f"📦 Книга {book_id} успешно возвращена.")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID выдачи.")
    except Exception as e:
        logger.error(f"Ошибка возврата: {e}")
        await update.message.reply_text(f"❌ Ошибка возврата: {e}")
    finally:
        conn.close()


# --- Автоматический возврат просроченных книг ---
async def check_overdue_books(context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()
    try:
        due_date = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
        cur.execute("SELECT id, book_id FROM loans WHERE return_date IS NULL AND issue_date <= ?", (due_date,))
        overdue_loans = cur.fetchall()

        for loan_id, book_id in overdue_loans:
            cur.execute("UPDATE loans SET return_date = ? WHERE id = ?", (datetime.now().strftime("%Y-%m-%d"), loan_id))
            cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
            conn.commit()
            logger.info(f"Автоматически возвращена книга {book_id}, выдача #{loan_id}")
    finally:
        conn.close()