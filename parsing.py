import time
import requests
from bs4 import BeautifulSoup
import convert
import re

URL_TIN = 'https://www.tinkoff.ru/invest/stocks/'
URL_GOO = "https://www.google.com/finance/quote/"
HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36','accept': '*/*'}

def get_html(url):
    """
    ## Получение html по ссылке
    """
    r = requests.get(url, headers = HEADER)
    print("Вывод get_html: ",r)
    return r

def get_content(html,name = ''):
    """
    ## Парсинг данных о акции из html файла

    Принимается html файл и не обязательный аргумент наименование тикера
    """
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find_all('div',class_ = 'Row-module__row_23MCP')
    acii1 = []
    for item in items:
        IO = item.find('span',class_ = 'SecurityHeaderPure__showName_1gpw6')
        #print(IO)
        if IO is None:
            print("Неверный тикер")
            acii1.append({
                'Name': name,
                'Cost': 'неверный тикер'
             })
        else:
            acii1.append({
                'Name':item.find('span',class_ = 'SecurityHeaderPure__showName_1gpw6').get_text(),
                #'Cost':item.find('span',class_ = 'Money-module__money_2PlRa').get_text(strip = True),
                'Cost':item.find('span',class_ = 'SecurityInvitingScreen__priceValue_1U3nL').get_text(strip = True),
                'Count': 0,
                'All_cost': 0
             })
    return acii1

def parse(t,bot,message,message_bot,url = URL_TIN):
    """
    ## Получение данных о акции(ях)

    ### Входные данные: 
    1) последовательность тикеров (t), html страницы которых парсятся и записываются в list (acii)

    ### Выходные данные
    1) list (acii), который хранит отдельные list для каждой акции
    """
    print("Parse: ON")
    count_ticker = len(t)
    html = get_html(url)
    if html.status_code == 200:
        acii = []
        for i in range(0,count_ticker):

            if int(count_ticker/2) == i:
                bot.edit_message_text('Осталось обработать чуть меньше половины \U0000231B',message.chat.id,message_bot.message_id)
            
            html = get_html(url+t[i].upper())
            acii.extend(get_content(html.text,t[i]))

        bot.edit_message_text(f'Все данные получены',message.chat.id,message_bot.message_id)
        print("Parse: OFF")
    else:
        print("Error")

    return acii

def acii_str_a(counter,p):
    """
    ## Запись всех акции в в одну строку (сообщение) 

    Создание "человеческого", приятного для глаз сообщения с информацией о акциях

    ### Входные данные:
    1) p - список, который хранит списки с информацией о акциях
    2) сounter - длинна p

    ### Возвращает
    одну форматированную строку
    """
    acii_str_all = ""
    b = 0 # Счётчик общей цены портфеля
    for i in range(0,counter):
        if p[i]["Cost"] == "неверный тикер": 
            acii_str = "".join(u'\U0000274C'+" "+'"'+p[i]["Name"]+'"'+' не верный тикер')
            acii_str_all +=acii_str +"\n" 
        elif p[i]["Count"] == 0:
            if p[i]["Cost"][-1] != '$':
                acii_str = "".join(u'\U00002705'+" "+p[i]["Name"]+" "+p[i]["Cost"]+ " (" + str(convert.conversion(p[i]["Cost"][-1],p[i]["Cost"][0:-1])) + "$ )")
            else:
                acii_str = "".join(u'\U00002705'+" "+p[i]["Name"]+" "+p[i]["Cost"])

            acii_str_all +=acii_str +"\n"   
        else:
            b += float(p[i]["All_cost"])
            p[i]['Cost'] = p[i]['Cost'].replace(',','.')
            if p[i]["Cost"][-1] != '$':
                acii_str = "".join(u'\U00002705'+" "+p[i]["Name"]+" "+p[i]["Cost"]  + " " + "(" + str(convert.conversion(p[i]["Cost"][-1],p[i]["Cost"][0:-1])) + "$ )"+"\n"+str(p[i]["Count"])+"шт"+" : "+str((p[i]["All_cost"]))+"$")
            else:
                acii_str = "".join(u'\U00002705'+" "+p[i]["Name"]+" "+p[i]["Cost"]  + " " +"\n"+str(p[i]["Count"])+ "шт"+" : "+str((p[i]["All_cost"]))+"$")

            acii_str_all +=acii_str +"\n"

    if b > 0: # Выполняется только в том случае если запрошено "Узнать цену"
        acii_str = "".join(f'Стоимость всего портфеля {convert.toFixed(b,1)} $')
        acii_str_all +=acii_str +"\n"

    if acii_str_all == None:
        acii_str_all = 1
        
    return acii_str_all

def tickers(bot,message):
    """
    ## Получение тикеров, обработка и отправка результатов

    Из сообщения принимаются введенные тикеры

    Функцией parse получаются данные о акциях

    Форматирование в читабельный вид с помощью функции acii_str_a

    Отправка результата в чат
    """
    '''Получение тикеров, обработка и отправка результатов'''
    t = message.text.split() # Тикеры, которые прислал пользователь
    message_bot = bot.send_message(message.chat.id,"Тикер(ы) приняты\n Ждите")
    print(f'Это тикер(ы) {t}')
    p = parse(t,bot,message,message_bot,URL_TIN)
    if not p:
        print("Список пуст, тикер неверный")
        bot.send_message(message.chat.id,"Неверный тикер")
    else:
        counter = len(p)
        a = acii_str_a(counter,p)
        bot.send_message(message.chat.id,a)

def get_content_price_value(html):
    """
    ## Парсинг данных о цене из html
    """
    soup = BeautifulSoup(html,'html.parser')
    items = soup.find('div',class_ = 'ln0Gqe').get_text()

    return items

def price_value(t = None):
    """
    ## Конвертация валют

    ### Принимает список содержащий:
    1) Валюты в виде из/в
    2) Цену акции

    ### Возвращает
    конвертированную цену с 2 цифрами после запятой
    """
    quantity_value = t [1] # количество вадюты
    value = re.split("/",t[0]) # валюты из/в
    ratio = '' # соотношение цен

    html = get_html(URL_GOO + value[0].upper() + '-' + value[1].upper())
    ratio = get_content_price_value(html.text)
    quantity_value = float(quantity_value) * float(ratio)

    return convert.toFixed(quantity_value,2)

