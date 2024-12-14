import telebot
from telebot import types
import random

TOKEN = '7161520921:AAGSuBtqfXEvhBX3GQPt0EmHZ7tZMuQXgP4'

"""Создание экземпляра бота"""
bot = telebot.TeleBot(TOKEN)

"""Хранилище данных о пользователях и их подарках"""
participants = {}

"""Состояние формирования группы"""
STATE_FORMING = "forming"

"""Состояние распределения подарков"""
STATE_DISTRIBUTING = "distributing"

"""Текущее состояние"""
current_state = STATE_FORMING

"""Обработчик команды /start"""
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global current_state
    current_state = STATE_FORMING
    bot.reply_to(message, "Привет! Это программа для тайного Санты. Начнем формирование группы. Добавьте участников с помощью команды /add.")

"""Обработчик команды /add"""
@bot.message_handler(commands=['add'])
def add_participant(message):
    global participants
    if current_state == STATE_FORMING:
        bot.reply_to(message, "Введите имя участника:")
        bot.register_next_step_handler(message, process_add_step)
    else:
        bot.reply_to(message, "Распределение подарков уже началось. Используйте команду /distribute, чтобы начать распределение подарков сначала.")

def process_add_step(message):
    global participants
    participant_name = message.text
    if participant_name:
        participants[participant_name] = {'gifts': []}
        bot.reply_to(message, f"Участник {participant_name} добавлен в группу.")
    if len(participants) >= 3:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add(types.KeyboardButton(text='Добавить следующего участника'))
        markup.add(types.KeyboardButton(text='Начать распределение подарков'))
        bot.reply_to(message, "Группа сформирована. Что вы хотите сделать?", reply_markup=markup)
    else:
        bot.reply_to(message, "Добавьте следующего участника, их пока меньше 3: /add")

"""Обработчик текстовых сообщений в состоянии формирования группы"""
@bot.message_handler(func=lambda message: current_state == STATE_FORMING)
def handle_forming(message):
    if message.text == 'Добавить следующего участника':
        bot.reply_to(message, "Введите имя участника:")
        bot.register_next_step_handler(message, process_add_step)
    elif message.text == 'Начать распределение подарков':
        if len(participants) >= 3:
            current_state = STATE_DISTRIBUTING
            bot.reply_to(message, "Начинаем распределение подарков.")
            distribute_gifts_automatically(message.chat.id)
    else:
        bot.reply_to(message, "Недостаточно участников для распределения подарков. Добавьте больше участников с помощью команды /add.")

"""Обработчик команды /distribute"""
@bot.message_handler(commands=['distribute'])
def distribute_gifts(message):
    if not can_distribute():
        bot.reply_to(message, "Распределение подарков уже началось.")
        return

    if len(participants) < 3:
        bot.reply_to(message, "Недостаточно участников для распределения подарков. Добавьте больше участников с помощью команды /add.")
        return

    start_distribution(message.chat.id)

def can_distribute():
    """Проверяет, можно ли начать распределение подарков."""
    return current_state == STATE_FORMING

def start_distribution(chat_id):
    """Начинает распределение подарков."""
    global current_state
    current_state = STATE_DISTRIBUTING
    bot.send_message(chat_id, "Начинаем распределение подарков.")
    distribute_gifts_automatically(chat_id)

def distribute_gifts_automatically(chat_id):
    global participants
    participant_names = list(participants.keys())
    random.shuffle(participant_names)
    for i in range(len(participant_names)):
        giver_name = participant_names[i]
        receiver_name = participant_names[(i + 1) % len(participant_names)]

        participants[receiver_name]['gifts'].append(giver_name)

        # Отправляем сообщение получателю подарка
        bot.send_message(chat_id, f"{giver_name} делает подарок {receiver_name}.")
"""Запуск бота"""
bot.polling()
