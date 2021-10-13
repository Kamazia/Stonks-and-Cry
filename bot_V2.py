import telebot
import time
import os
import bmemcached
import sys
import re
import keyboard # Модуль с клавиатурами
import text # Модуль с текстами сообщений
import parsing # Модуль с функциями для парсинга
import portfolio_actions # Модуль с функциями-действиями над портфелем
from bs4 import BeautifulSoup
from telebot.types import BotCommand

client = bmemcached.Client(os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','), os.environ.get('MEMCACHEDCLOUD_USERNAME'), os.environ.get('MEMCACHEDCLOUD_PASSWORD'))
URL = 'https://www.tinkoff.ru/invest/stocks/'
HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36','accept': '*/*'}

bot_token = os.environ["bot_token"]
commands = [
    BotCommand("start","Начало"),
    BotCommand("help","Список команд"),
    BotCommand("tiker","Тикер акции"),
    BotCommand("portfolio","Портфель")
    ]

def check_spam(bot,message,last_time,check_msg):
    """
    ## Функция блокировки спамеров
    При отправле более 4 сообщений за 2.5 sec в memcached помещается флаг 1, который через час удалится автоматически

    Если пользователь заблокирован бот ему не отвечает
    """
    if client.get(str(message.chat.id)+'_ban') == 1: # Если флаг == 1, значит у пользователя бан
        return False

    elif message.chat.id not in last_time: # Если в last_time нет времени отправки последнего сообщения, то мы его записываем и ставим флаг номера сообщения
        last_time[message.chat.id] = time.time()
        check_msg[message.chat.id] = 1
        return True

    elif (time.time() - last_time[message.chat.id]) < 2.5: # Если между отправками сообщений прошло меньше 2.5 sec инкрементируем check_msg
        check_msg[message.chat.id] += 1
        if check_msg[message.chat.id] == 4: # Если за 2.5 sec отправлено больше 4 сообщений выдается бан (флаг = 1), через час флаг удалится из базы
            client.set(str(message.chat.id)+'_ban',1,3600)
            bot.send_message(message.chat.id,'Вам выдан бан на 1 час за спам')
            print(f'Заблокирован пользователь *{message.from_user.first_name}({message.from_user.username})*({message.chat.id})')
            del check_msg[message.chat.id]
            del last_time[message.chat.id]
        pass

    else: # Если флаг != 1 и с момента отправки сообщения прошло > 2.5 sec, то обновляем время последнего сообщения и счётчик сообщений
        last_time[message.chat.id] = time.time()
        check_msg[message.chat.id] = 1
        return True

def teleg_bot(bot_token):
    """
    ## Главная функция бота

    Содержит вызовы функций

    Принимает значение токена

    Работает по средствам polling без остановки и с интервалом обращения 0
    """
    bot = telebot.TeleBot(bot_token,threaded = True, num_threads = 4)
    bot.set_my_commands(commands)
    print("bot is running")

    @bot.callback_query_handler(func = lambda call: True)
    def query_handler(call):
        bot.answer_callback_query(call.id, text="OK")
        if call.data == 'cancel':
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.edit_message_text(text.message_portfolio,call.message.chat.id, call.message.message_id, reply_markup = keyboard.menu_stock())
            
        elif call.data == 'edit':
            message_bot = bot.edit_message_text(text.message_edit, call.message.chat.id, call.message.message_id, reply_markup = keyboard.cancel_menu(), parse_mode = "HTML")
            bot.register_next_step_handler(call.message, lambda message: portfolio_actions.edit(bot, message, message_bot))

        elif call.data == 'add':
            if client.get(str(call.message.chat.id)+'_my') is not None:
                bot.edit_message_text(text.message_add, call.message.chat.id, call.message.message_id, reply_markup = keyboard.menu_stock())
            else:
                message_bot = bot.edit_message_text(text.message_add_another, call.message.chat.id, call.message.message_id, reply_markup = keyboard.cancel_menu(), parse_mode = "HTML")
                bot.register_next_step_handler(call.message, lambda message: portfolio_actions.save(bot,message,message_bot))

        elif call.data == 'cost':
            portfolio_data = client.get(str(call.message.chat.id)+'_my') # Получение строки с name/cost акций пользователя
            if portfolio_data is None:
                bot.edit_message_text("\U00002B55Вы ещё не добавили акции в портфель\n"+text.message_portfolio, call.message.chat.id, call.message.message_id, reply_markup = keyboard.menu_stock())
            else:
                bot.delete_message(call.message.chat.id,call.message.message_id)
                portfolio_actions.cost(bot,portfolio_data,call.message)


    @bot.message_handler(commands = ['start'])
    def start_msg(message):
        if check_spam(bot,message,last_time,check_msg) is True: # Проверка на спам сообщениями
            bot.send_message(message.chat.id, text.message_start)

    @bot.message_handler(commands = ['help'])
    def help_msg(message):
        if check_spam(bot,message,last_time,check_msg) is True: # Проверка на спам сообщениями
            bot.send_message(message.chat.id, text.message_help, parse_mode = "HTML")

    @bot.message_handler(commands = ['tiker'])
    def tiker(message):
        if check_spam(bot,message,last_time,check_msg) is True: # Проверка на спам сообщениями
            bot.send_message(message.chat.id,"Введите тикер")
            bot.register_next_step_handler(message, lambda message: parsing.tickers(bot,message))

    @bot.message_handler(commands = ['portfolio'])
    def portfolio(message):
        if check_spam(bot,message,last_time,check_msg) is True: # Проверка на спам сообщениями
            bot.send_message(message.chat.id, text.message_portfolio, reply_markup = keyboard.menu_stock())

    @bot.message_handler(content_types = ['text'])
    def send_text(message):
        if len(last_time) == 100: # При достижении 100 пар (user_id: время последнего сообщения) отчистить словарь
            print(f"Отчищен список занимающий {sys.getsizeof(last_time)+sys.getsizeof(check_msg)} байта")
            last_time.clear(),check_msg.clear()

        bot.send_message(message.chat.id,"Воcпользуйтесь меню команд или введите /help")

    bot.polling(none_stop = True, interval = 0)

if __name__ == '__main__':
    last_time = {} # Для хранения -> user_id: время последнего сообщения
    check_msg = {} # Счётчик кол-ва сообщений
    teleg_bot(bot_token)