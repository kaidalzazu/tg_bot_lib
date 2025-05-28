# bot.py

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv
import os
import logging
from handlers import book_handlers, reader_handlers, loan_handlers
import sqlite3
# Логирование
logging.basicConfig(
    filename='logs.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Главная клавиатура
from config import MAIN_MENU, STATE_AWAITING_ISSUE, STATE_AWAITING_RETURN

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт бота"""
    await reader_handlers.register_reader(update, context)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get('state')

    # --- Регистрация пользователя ---
    if state == "register":
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("❌ Введите ФИО и группу через пробел.\nПример: Иван Иванов ИВТ-23")
            return

        name = ' '.join(parts[:2])
        group = ' '.join(parts[2:])
        telegram_id = update.effective_user.id

        conn = None
        try:
            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO readers(telegram_id, name, group_department) VALUES(?,?,?)",
                        (telegram_id, name, group))
            conn.commit()
            await update.message.reply_text(f"✅ Привет, {name} из {group}!")
            await update.message.reply_text("Выберите действие:", reply_markup=MAIN_MENU)
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
        finally:
            if conn:
                conn.close()

    # --- Получить книгу ---
    elif context.user_data.get('state') == STATE_AWAITING_ISSUE:
        try:
            book_id = int(text)
            context.args = [str(book_id)]
            await loan_handlers.issue_book(update, context)
            context.user_data.pop('state', None)
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID книги.", reply_markup=MAIN_MENU)

    # --- Вернуть книгу ---
    elif context.user_data.get('state') == STATE_AWAITING_RETURN:
        try:
            loan_id = int(text)
            context.args = [str(loan_id)]
            await loan_handlers.return_book(update, context)
            context.user_data.pop('state', None)
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID выдачи.", reply_markup=MAIN_MENU)

    # --- Кнопки меню ---
    elif text == "📚 Доступные книги":
        await book_handlers.list_books(update, context)

    elif text == "📖 Мои книги":
        await loan_handlers.my_books(update, context)

    elif text == "📦 Получить книгу":
        await update.message.reply_text("Введите ID книги для выдачи:")
        context.user_data['state'] = STATE_AWAITING_ISSUE

    elif text == "⮿ Вернуть книгу":
        await update.message.reply_text("Введите ID выдачи для возврата:")
        context.user_data['state'] = STATE_AWAITING_RETURN

    else:
        await update.message.reply_text("Выберите действие из меню.", reply_markup=MAIN_MENU)


# --- Точка входа ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("books", book_handlers.list_books))
    app.add_handler(CommandHandler("add_book", book_handlers.add_book))
    app.add_handler(CommandHandler("my_books", loan_handlers.my_books))
    app.add_handler(CommandHandler("issue", loan_handlers.issue_book))
    app.add_handler(CommandHandler("return", loan_handlers.return_book))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()