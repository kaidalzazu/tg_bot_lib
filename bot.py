from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os
import logging
from handlers import book_handlers
from handlers import reader_handlers
from handlers import loan_handlers

# Логирование ошибок
logging.basicConfig(
    filename='logs.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# --- СОСТОЯНИЯ ---
STATE_REGISTER = "register"

# --- ОСНОВНЫЕ ФУНКЦИИ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    registered = await reader_handlers.register_reader(update, context)

    if not registered:
        # Переход в состояние регистрации
        context.user_data['state'] = STATE_REGISTER
    else:
        context.user_data.clear()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')

    if state == STATE_REGISTER:
        text = update.message.text.strip()
        parts = text.split()
        if len(parts) < 3:
            await update.message.reply_text("❌ Введите ФИО и группу через пробел.\nПример: Иван Иванов ИВТ-23")
            return

        name = ' '.join(parts[:2])
        group = ' '.join(parts[2:])

        conn = None
        try:
            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO readers(telegram_id, name, group_department) VALUES(?,?,?)",
                        (update.effective_user.id, name, group))
            conn.commit()
            await update.message.reply_text(f"✅ Привет, {name} из {group}!", reply_markup=loan_handlers.MAIN_MENU)
            context.user_data.clear()
        except Exception as e:
            logger.error(f"Ошибка регистрации: {e}")
            await update.message.reply_text("❌ Ошибка регистрации.")
        finally:
            if conn:
                conn.close()
    elif update.message.text.lower() == "📦 получить книгу":
        await update.message.reply_text("Введите ID книги:")
    elif update.message.text.lower() == "⮿ вернуть книгу":
        await update.message.reply_text("Введите ID выдачи (не ID книги):")
    elif update.message.text.lower() == "📚 доступные книги":
        await book_handlers.list_books(update, context)
    elif update.message.text.lower() == "📖 мои книги":
        await loan_handlers.my_books(update, context)
    else:
        await update.message.reply_text("Выберите действие из меню.", reply_markup=loan_handlers.MAIN_MENU)

# --- ЗАПУСК БОТА ---

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("books", book_handlers.list_books))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()