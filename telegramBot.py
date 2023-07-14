import telebot
import datetime
import csv`
import pytz
from telebot import types

# Создаем экземпляр бота
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# Словарь для хранения данных о рабочем времени
work_hours = {}

# Словарь для хранения данных о выбранных днях работы
selected_days = {}

# Словарь для хранения данных о пользователях
users = {}


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для записи рабочего времени. Чтобы начать, отправь мне свое имя.")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def record_work_time(message):
    try:
        # Проверяем, что пользователь уже ввел свое имя
        if message.chat.id not in users:
            # Сохраняем имя пользователя
            users[message.chat.id] = message.text
            bot.reply_to(message,
                         f"Привет, {message.text}! Теперь отправь мне день недели и количество отработанных часов в формате 'День:Часы'.")
        else:
            # Разделяем сообщение на день недели и количество часов
            day, hours = message.text.split(':')

            # Проверяем, что введенное время является числом
            hours = float(hours)

            # Проверяем, что введенное время положительное
            if hours < 0:
                raise ValueError

            # Получаем текущую дату
            today = datetime.date.today()

            # Проверяем, что введенный день недели является корректным
            if day.lower() not in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']:
                raise ValueError

            # Добавляем запись о рабочем времени в словарь
            if today not in work_hours:
                work_hours[today] = {}
            work_hours[today][day.lower()] = hours

            bot.reply_to(message, "Время успешно записано!")

    except ValueError:
        bot.reply_to(message, "Некорректный формат времени. Пожалуйста, используйте формат 'День:Часы'.")


# Обработчик команды /завершить
@bot.message_handler(commands=['завершить'])
def finish_work(message):
    try:
        # Получаем текущую дату
        today = datetime.date.today()

        # Проверяем, что для текущей даты есть записи о рабочем времени
        if today not in work_hours or len(work_hours[today]) == 0:
            raise ValueError

        # Считаем общее количество отработанных часов и заработанную сумму
        total_hours = sum(work_hours[today].values())
        total_earnings = total_hours * YOUR_HOURLY_RATE  # Замените YOUR_HOURLY_RATE на вашу почасовую ставку

        # Сохраняем данные в общую таблицу
        with open('work_hours.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([today, total_hours, total_earnings, users[message.chat.id]])

        # Очищаем словарь с данными о рабочем времени
        work_hours[today] = {}

        bot.reply_to(message, f"Рабочее время успешно завершено. Заработано: {total_earnings} рублей.")

    except ValueError:
        bot.reply_to(message, "Нет записей о рабочем времени для текущей даты.")


# Обработчик команды /выбратьдень
@bot.message_handler(commands=['выбратьдень'])
def select_work_day(message):
    try:
        # Создаем клавиатуру с кнопками для выбора дня недели
        keyboard = types.ReplyKeyboardMarkup(row_width=7, one_time_keyboard=True)
        days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        buttons = [types.KeyboardButton(day) for day in days]
        keyboard.add(*buttons)

        # Отправляем сообщение с клавиатурой
        bot.reply_to(message, "Выберите день недели, когда вы будете работать:", reply_markup=keyboard)

        # Устанавливаем состояние пользователя в ожидание выбора дня
        bot.register_next_step_handler(message, process_selected_day)

    except Exception as e:
        bot.reply_to(message, "Произошла ошибка. Пожалуйста, попробуйте еще раз.")


# Обработчик выбранного дня
def process_selected_day(message):
    try:
        # Получаем выбранный день
        selected_day = message.text.lower()

        # Проверяем, что выбранный день является корректным
        if selected_day not in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']:
            raise ValueError

        # Получаем текущую дату
        today = datetime.date.today()

        # Получаем текущее время
        current_time = datetime.datetime.now(pytz.timezone('Europe/Moscow')).time()

        # Получаем дату выбранного дня
        selected_date = today + datetime.timedelta(days=(days.index(selected_day) - today.weekday()) % 7)

        # Устанавливаем напоминание за 8 часов до начала рабочего дня
        reminder_time = datetime.datetime.combine(selected_date, datetime.time(hour=8)) - datetime.timedelta(hours=8)

        # Проверяем, что напоминание еще не установлено
        if selected_date not in selected_days:
            selected_days[selected_date] = reminder_time

        # Отправляем напоминание
        bot.send_message(message.chat.id,
                         f"Напоминание: через 8 часов начнется рабочий день в {selected_day.capitalize()}.")

    except ValueError:
        bot.reply_to(message,
                     "Некорректный выбранный день. Пожалуйста, выберите день недели из предложенных вариантов.")


# Обработчик команды /сводка
@bot.message_handler(commands=['сводка'])
def generate_summary(message):
    try:
        # Получаем текущую дату
        today = datetime.date.today()

        # Проверяем, что прошло четыре дня с последней сводки
        if today not in selected_days or (today - selected_days[today]).days < 4:
            raise ValueError

        # Считаем общее количество отработанных часов и заработанную сумму за последние четыре дня
        total_hours = 0
        total_earnings = 0
        for date, hours in work_hours.items():
            if (today - date).days <= 4:
                total_hours += sum(hours.values())
                total_earnings += sum(
                    hours.values()) * YOUR_HOURLY_RATE  # Замените YOUR_HOURLY_RATE на вашу почасовую ставку

        # Считаем количество работников
        total_employees = len(users)

        bot.reply_to(message,
                     f"Сводка за последние четыре дня:\n\nКоличество работников: {total_employees}\nОбщее количество отработанных часов: {total_hours}\nОбщая заработанная сумма: {total_earnings} рублей.")

    except ValueError:
        bot.reply_to(message, "Нет данных для составления сводки.")


# Обработчик команды /инструкция
@bot.message_handler(commands=['инструкция'])
def show_instructions(message):
    instructions = """
    Инструкция по использованию бота для записи рабочего времени:

    1. Запустите бота командой /start.
    2. Введите свое имя.
    3. Отправьте боту день недели и количество отработанных часов в формате 'День:Часы'.
    4. Для завершения рабочего дня используйте команду /завершить.
    5. Чтобы выбрать день недели, когда вы будете работать, используйте команду /выбратьдень.
    6. Для получения сводки за последние четыре дня используйте команду /сводка.
    7. Чтобы получить инструкцию по использованию бота, используйте команду /инструкция.

    Пожалуйста, не забудьте заменить `YOUR_TELEGRAM_BOT_TOKEN` на токен вашего телеграм-бота и `YOUR_HOURLY_RATE` на вашу почасовую ставку. Также, убедитесь, что у вас установлен модуль `telebot` для работы с Telegram API, модуль `csv` для работы с CSV файлами и модуль `pytz` для работы с часовыми поясами.
    """
    bot.reply_to(message, instructions)


# Обработчик команды /начатьдень
@bot.message_handler(commands=['начатьдень'])
def start_work_day(message):
    try:
        # Получаем текущую дату
        today = datetime.date.today()

        # Проверяем, что для текущей даты нет записей о рабочем времени
        if today in work_hours and len(work_hours[today]) > 0:
            raise ValueError

        # Отправляем сообщение о начале рабочего дня
        bot.reply_to(message, "Рабочий день начат!")

    except ValueError:
        bot.reply_to(message, "Рабочий день уже начат или есть записи о рабочем времени для текущей даты.")


# Запускаем бота
bot.polling()