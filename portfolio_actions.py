import re
import bot_V2
import convert
import parsing

def cost(bot,portfolio_data,message):
    """
    ## Получение цен на акции пользователя из портфеля

    ### Входные данные:
    1) Список значений вида наименование/количество (spce/10)

    ### Результат работы:
    1) Отправляет форматированное сообщение с ценами пользователю
    """
    name_stock = [] # Список хранящий названия акций пользователя
    quantity_stock = [] # Список хранящий количество акций пользователя
    for i in range (0,len(portfolio_data)):
        division_portfolio_data = re.split("/",portfolio_data[i]) # Отделение названия от цены (name/cost)
        if len(division_portfolio_data) == 2:
            try:
                int(division_portfolio_data[1])
            except ValueError:
                division_portfolio_data[1] = ''
        if len(division_portfolio_data) != 2 or division_portfolio_data[0] == '' or division_portfolio_data[1] == '':
            pass
        else:
            name_stock.append(division_portfolio_data[0].upper())
            quantity_stock.append(division_portfolio_data[1])
    if not name_stock:
        print("Список пуст, данные не верны")
        bot.send_message(message.chat.id,"Неверные данные")
    else:
        message_bot = bot.send_message(message.chat.id,"Чичас всё будет \U0001F44C")
        p = parsing.parse(name_stock,bot, message,message_bot)
        counter = len(p)
        for i in range(0,counter):
            if p[i]['Cost'] != "неверный тикер":
                share_price = p[i]['Cost'].replace(',','.')
                currency = share_price[-1]
                share_price = convert.conversion(currency,share_price[0:-1]) # конвертация цены
                sum_price = float(share_price) * int(quantity_stock[i]) # общая цена акции в портфеле
                p[i]['Count'] = int(quantity_stock[i])
                p[i]['All_cost'] = convert.toFixed(sum_price,1)
            else:
                pass
        a = parsing.acii_str_a(counter,p) # форматирование
        bot.send_message(message.chat.id, a) 

def save(bot,message,message_bot):
    """
    ## Сохранение акций портфеля в БД

    ### Входные данные:
    1) Сообщение пользователя с акциями в виде перечисления наименование/количество
    2) Предыдущие сообщение бота для удаления

    ### Результат работы:
    1) Добаление акций в memchached
    2) Вывод цены на акции добаленные в портфель
    """
    bot.delete_message(message.chat.id, message_bot.message_id)

    t = message.text.split()
    bot_V2.client.add(str(message.chat.id)+'_my',t,2592000)
    bot.send_message(message.chat.id,"Акции добавлены")

    portfolio_data = bot_V2.client.get(str(message.chat.id)+'_my')
    cost(bot,portfolio_data,message)

def edit(bot,message,message_bot):
    """
    ## Изменение акций портфеля в БД

    ### Входные данные:
    1) Сообщение пользователя с акциями в виде перечисления наименование/количество
    2) Предыдущие сообщение бота для удаления

    ### Результат работы:
    1) Изменение акций в memchached
    2) Вывод цены на новых акций добаленных в портфель
    """
    bot.delete_message(message.chat.id, message_bot.message_id)

    t = message.text.split()
    bot_V2.client.set(str(message.chat.id)+'_my',t,2592000)
    bot.send_message(message.chat.id,"Акции изменены")

    portfolio_data = bot_V2.client.get(str(message.chat.id)+'_my')
    cost(bot,portfolio_data,message)