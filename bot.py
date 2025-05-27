<<<<<<< HEAD
# bot.py - Telegram бот "Библиотекарь Колледжа"

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    JobQueue,
)
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from handlers import book_handlers, reader_handlers, loan_handlers
import os
import logging

# --- Логирование ---
logging.basicConfig(
    filename='logs.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

# --- Загрузка токена ---
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- Клавиатура снизу ---
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [["📚 Доступные книги", "📖 Мои книги"],
     ["📦 Получить книгу", "⮿ Вернуть книгу"]],
    resize_keyboard=True
)
=======
import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
>>>>>>> b4c1024b3ff478b9e5ce624bf0e331f32f15d4de

dp = Dispatcher()

<<<<<<< HEAD
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Старт бота + регистрация читателя"""
    user = update.effective_user
    registered = await reader_handlers.register_reader(update, context)

    if registered:
        await update.message.reply_text(f"Добро пожаловать в библиотеку, {user.full_name}!")
        await update.message.reply_text("Выберите действие:", reply_markup=MAIN_MENU_KEYBOARD)
    else:
        # Ждём ФИО и группу
        await update.message.reply_text("Введите ваше ФИО и группу через пробел.\nПример: Иван Иванов ИВТ-23")
        context.user_data['state'] = 'register'


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get('state')

    # --- Регистрация пользователя ---
    if state == "register":
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("❌ Введите ФИО и группу через пробел.")
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
            await update.message.reply_text("Выберите действие:", reply_markup=MAIN_MENU_KEYBOARD)
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            await update.message.reply_text(f"❌ Ошибка регистрации: {e}")
        finally:
            if conn:
                conn.close()

    # --- Ввод ID книги ---
    elif context.user_data.get('awaiting_issue'):
        try:
            book_id = int(text)
            context.user_data.pop('awaiting_issue', None)
            context.args = [str(book_id)]
            await loan_handlers.issue_book(update, context)
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID книги. Введите число.")

    # --- Ввод ID выдачи ---
    elif context.user_data.get('awaiting_return'):
        try:
            loan_id = int(text)
            context.user_data.pop('awaiting_return', None)
            context.args = [str(loan_id)]
            await loan_handlers.return_book(update, context)
        except ValueError:
            await update.message.reply_text("❌ Неверный формат ID выдачи. Введите число.")

    # --- Кнопки меню ---
    elif text == "📚 Доступные книги":
        await book_handlers.list_books(update, context)
    elif text == "📖 Мои книги":
        await loan_handlers.my_books(update, context)
    elif text == "📦 Получить книгу":
        await update.message.reply_text("Введите ID книги для выдачи:")
        context.user_data['awaiting_issue'] = True
    elif text == "⮿ Вернуть книгу":
        await update.message.reply_text("Введите ID выдачи для возврата:")
        context.user_data['awaiting_return'] = True
    else:
        await update.message.reply_text("Выберите действие из меню.", reply_markup=MAIN_MENU_KEYBOARD)


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

    job_queue = app.job_queue
    if job_queue:
        from handlers.loan_handlers import check_overdue_books
        job_queue.run_repeating(check_overdue_books, interval=86400, first=0)

    print("Бот запущен...")
    app.run_polling()


if __name__ == '__main__':
    main()
=======

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command('openWindow'))
async def command_openWindow_handler(message: Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Open',
                    web_app=WebAppInfo(url=f'https://www.google.co.uk/'),
                )
            ]
        ]
    )
    await message.answer("Start", reply_markup=markup)

@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
>>>>>>> b4c1024b3ff478b9e5ce624bf0e331f32f15d4de
