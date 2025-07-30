import json
import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

DATA_FILE = "user_subscriptions.json"
ADMIN_IDS = [468994162]

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Используй /subscribe YYYY-MM-DD чтобы сохранить дату окончания подписки.")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    if not context.args:
        await update.message.reply_text("Укажи дату окончания подписки. Пример: /subscribe 2025-08-15")
        return
    try:
        end_date = context.args[0]
        datetime.strptime(end_date, "%Y-%m-%d")
        data = load_data()
        data[user_id] = end_date
        save_data(data)
        await update.message.reply_text(f"Дата окончания подписки сохранена: {end_date}")
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Используй: /subscribe 2025-08-15")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("У тебя нет доступа к этой команде.")
        return
    data = load_data()
    if not data:
        await update.message.reply_text("Нет сохранённых пользователей.")
        return
    message = "📋 Список подписчиков:\n"
    for uid, date in data.items():
        message += f"👤 {uid} — до {date}\n"
    await update.message.reply_text(message)

async def check_subscriptions(application):
    while True:
        today = datetime.now().date()
        data = load_data()
        for user_id, end_date_str in data.items():
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                if end_date - today == timedelta(days=3):
                    await application.bot.send_message(chat_id=int(user_id),
                        text=f"🔔 Напоминание: Ваша подписка заканчивается через 3 дня ({end_date})!")
            except Exception as e:
                print(f"Ошибка для пользователя {user_id}: {e}")
        await asyncio.sleep(86400)

async def main():
    app = ApplicationBuilder().token("8169403134:AAGsWrSYeaFsTDC2VRYyTP5JjTWQbwmEt6Y").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("list", list_users))

    asyncio.create_task(check_subscriptions(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())