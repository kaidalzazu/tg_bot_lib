# handlers/loan_handlers.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import sqlite3
import logging

logger = logging.getLogger(__name__)

# --- Импортируем MAIN_MENU ---
try:
    from config import MAIN_MENU, STATE_AWAITING_ISSUE, STATE_AWAITING_RETURN
except ImportError:
    logger.critical("❌ Не найден файл config.py")
    raise

# --- Выдача книги ---
async def issue_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID книги для выдачи:")
        context.user_data['state'] = STATE_AWAITING_ISSUE
        return

    try:
        book_id = int(args[0])
        telegram_id = update.effective_user.id
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        # Проверяем доступность книги
        cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
        qty_row = cur.fetchone()
        if not qty_row or qty_row[0] <= 0:
            await update.message.reply_text("❌ Эта книга недоступна.", reply_markup=MAIN_MENU)
            return

        # Проверяем регистрацию пользователя
        cur.execute("SELECT id FROM readers WHERE telegram_id=?", (telegram_id,))
        reader_row = cur.fetchone()
        if not reader_row:
            await update.message.reply_text("❌ Сначала зарегистрируйтесь через /start", reply_markup=MAIN_MENU)
            return

        reader_id = reader_row[0]
        today = datetime.now().strftime("%Y-%m-%d")

        # Выдаём книгу
        cur.execute("INSERT INTO loans(book_id, reader_id, issue_date) VALUES(?,?,?)",
                    (book_id, reader_id, today))
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id=?", (book_id,))
        conn.commit()
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        await update.message.reply_text(f"✅ Книга {book_id} выдана до {due}.", reply_markup=MAIN_MENU)
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID книги.", reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Ошибка при выдаче: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}", reply_markup=MAIN_MENU)
    finally:
        conn.close()


# --- Возврат книги ---
async def return_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID выдачи для возврата:")
        context.user_data['state'] = STATE_AWAITING_RETURN
        return

    try:
        loan_id = int(args[0])
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        cur.execute("SELECT book_id FROM loans WHERE id=? AND return_date IS NULL", (loan_id,))
        res = cur.fetchone()
        if not res:
            await update.message.reply_text("❌ Такой выдачи не существует или она уже возвращена.", reply_markup=MAIN_MENU)
            return

        book_id = res[0]
        today = datetime.now().strftime("%Y-%m-%d")

        cur.execute("UPDATE loans SET return_date = ? WHERE id = ?", (today, loan_id))
        cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
        conn.commit()
        await update.message.reply_text(f"📦 Книга {book_id} успешно возвращена.", reply_markup=MAIN_MENU)
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID выдачи. Введите число.", reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Ошибка возврата: {e}")
        await update.message.reply_text(f"❌ Ошибка возврата: {e}", reply_markup=MAIN_MENU)
    finally:
        conn.close()


# --- Список моих книг ---
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
        await update.message.reply_text(msg or "У вас пока нет книг.", reply_markup=MAIN_MENU)
    except Exception as e:
        logger.error(f"Ошибка получения списка книг: {e}")
        await update.message.reply_text("❌ Ошибка загрузки данных.")
    finally:
        if conn:
            conn.close()