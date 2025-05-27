from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
import sqlite3
from datetime import datetime, timedelta

# Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["📚 Доступные книги", "📖 Мои книги"],
     ["📦 Получить книгу", "⮿ Вернуть книгу"]],
    resize_keyboard=True
)


async def my_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список книг, выданных текущему пользователю"""
    user_id = update.effective_user.id
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    try:
        cur.execute("""SELECT l.id, b.title, l.issue_date
                       FROM loans l
                                JOIN books b ON l.book_id = b.id
                       WHERE l.reader_id = (SELECT id FROM readers WHERE telegram_id = ?)
                         AND l.return_date IS NULL""",
                    (user_id,))
        rows = cur.fetchall()
        msg = "📖 Ваши книги:\n"
        for row in rows:
            msg += f"Выдача #{row[0]} — {row[1]} (выдана {row[2]})\n"
        await update.message.reply_text(msg or "У вас пока нет книг.", reply_markup=MAIN_MENU)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении списка книг: {e}", reply_markup=MAIN_MENU)
    finally:
        conn.close()


async def issue_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выдаёт книгу читателю по ID книги"""
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID книги для выдачи:")
        return

    try:
        book_id = int(args[0])
        user_id = update.effective_user.id
        conn = sqlite3.connect('library.db')
        cur = conn.cursor()

        # Получаем reader_id по telegram_id
        cur.execute("SELECT id FROM readers WHERE telegram_id=?", (user_id,))
        reader_row = cur.fetchone()
        if not reader_row:
            await update.message.reply_text("❌ Вы не зарегистрированы. Используйте /start", reply_markup=MAIN_MENU)
            return

        reader_id = reader_row[0]

        # Проверяем наличие книги
        cur.execute("SELECT quantity FROM books WHERE id=?", (book_id,))
        qty_row = cur.fetchone()
        if not qty_row or qty_row[0] <= 0:
            await update.message.reply_text("❌ Эта книга недоступна.", reply_markup=MAIN_MENU)
            return

        # Выдаём книгу
        today = datetime.now().strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        cur.execute("INSERT INTO loans(book_id, reader_id, issue_date) VALUES(?,?,?)",
                    (book_id, reader_id, today))
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id=?", (book_id,))
        conn.commit()
        await update.message.reply_text(f"✅ Книга {book_id} выдана до {due}.", reply_markup=MAIN_MENU)
    except ValueError:
        await update.message.reply_text("❌ Неверный формат ID книги. Введите число.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при выдаче: {e}", reply_markup=MAIN_MENU)
    finally:
        conn.close()


async def return_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает книгу по ID выдачи"""
    args = context.args
    if not args:
        await update.message.reply_text("Введите ID выдачи для возврата:")
        return