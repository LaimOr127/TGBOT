#Телеграм бот для работы и ведения отчетности (в моем случае для работы с SUP-досками)

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
from datetime import datetime, timedelta

# создание экземпляра класса Updater и передача токена бота
updater = Updater(token='TELEGRAM_BOT_TOKEN', use_context=True)

# функция для обработки команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите пароль для начала рабочего дня:")

# функция для обработки команды /end
def end(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Рабочий день завершен. Спасибо за работу!")

# функция для обработки сообщения с информацией о клиенте
def record_customer(update, context):
    if context.user_data.get("password"):
        message = update.message.text
        # запись информации о клиенте в базу данных
        client = FaunaClient(secret="FAUNADB_SECRET_KEY")
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        user_id = update.effective_chat.id
        name, paid, number = message.split(",")
        client.query(
            q.create(
                q.collection("customers"),
                {"data": {"day": current_date, "time": current_time, "name": name.strip(), "paid": int(paid.strip()), "number": number.strip(), "user_id": user_id}}
            )
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text="Информация о клиенте записана.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Введите пароль для начала рабочего дня.")

# функция для создания таблицы с информацией о клиентах и отправки ее пользователю
def view_table(update, context):
    client = FaunaClient(secret="FAUNADB_SECRET_KEY")
    user_id = update.effective_chat.id
    result = client.query(
        q.map_(
            lambda x: q.get(x),
            q.paginate(q.match(q.index("all_customers_by_user_id"), user_id))
        )
    )
    data = [r["data"] for r in result["data"]]
    df = pd.DataFrame(data)
    table = df.to_string(index=False)
    total_customers = len(df)
    total_paid = df["paid"].sum()
    context.bot.send_message(chat_id=update.effective_chat.id, text=table)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Всего клиентов: {total_customers}. Всего оплачено: {total_paid} руб.")

# функция для отправки недельной таблицы
def send_weekly_table(context):
    client = FaunaClient(secret="FAUNADB_SECRET_KEY")
    current_date = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = client.query(
        q.map_(
            lambda x: q.get(x),
            q.paginate(q.range(q.match(q.index("all_customers_by_date")), week_ago, current_date))
        )
    )
    data = [r["data"] for r in result["data"]]
    df = pd.DataFrame(data)
    table = df.to_string(index=False)
    total_customers = len(df)
    total_paid = df["paid"].sum()
    context.bot.send_message(chat_id="CHAT_ID", text=table)  # Замените "CHAT_ID" на идентификатор чата, куда нужно отправить таблицу
    context.bot.send_message(chat_id="CHAT_ID", text=f"Всего клиентов: {total_customers}. Всего оплачено: {total_paid} руб.")  # Замените "CHAT_ID" на идентификатор чата, куда нужно отправить итоговую сумму

# функция для объединения таблиц нескольких пользователей
def merge_tables(context):
    client = FaunaClient(secret="FAUNADB_SECRET_KEY")
    current_date = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = client.query(
        q.map_(
            lambda x: q.get(x),
            q.paginate(q.range(q.match(q.index("all_customers_by_date")), week_ago, current_date))
        )
    )
    data = [r["data"] for r in result["data"]]
    df = pd.DataFrame(data)
    table = df.to_string(index=False)
    context.bot.send_message(chat_id="CHAT_ID", text=table)  # Замените "CHAT_ID" на идентификатор чата, куда нужно отправить таблицу

# функция для обработки команды /day
def view_day_table(update, context):
    client = FaunaClient(secret="FAUNADB_SECRET_KEY")
    user_id = update.effective_chat.id
    current_date = datetime.now().strftime("%Y-%m-%d")
    result = client.query(
        q.map_(
            lambda x: q.get(x),
            q.paginate(q.intersection(q.match(q.index("all_customers_by_user_id"), user_id), q.match(q.index("all_customers_by_date"), current_date)))
        )
    )
    data = [r["data"] for r in result["data"]]
    df = pd.DataFrame(data)
    table = df.to_string(index=False)
    total_customers = len(df)
    total_paid = df["paid"].sum()
    context.bot.send_message(chat_id=update.effective_chat.id, text=table)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Всего клиентов: {total_customers}. Всего оплачено: {total_paid} руб.")

def create_buttons(update, context):
    keyboard = [
        [InlineKeyboardButton("Просмотреть таблицу", callback_data="view_table")],
        [InlineKeyboardButton("Отправить недельную таблицу", callback_data="send_weekly_table")],
        [InlineKeyboardButton("Объединить таблицы", callback_data="merge_tables")],
        [InlineKeyboardButton("Просмотреть таблицу за день", callback_data="view_day_table")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите действие:", reply_markup=reply_markup)

def button_handler(update, context):
    query = update.callback_query
    if query.data == "view_table":
        view_table(update, context)
    elif query.data == "send_weekly_table":
        send_weekly_table(context)
    elif query.data == "merge_tables":
        merge_tables(context)
    elif query.data == "view_day_table":
        view_day_table(update, context)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("end", end))
updater.dispatcher.add_handler(CommandHandler("password", enter_password))
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, record_customer))
updater.dispatcher.add_handler(CallbackQueryHandler(button_handler))

updater.start_polling()
