import re
import parsing

def toFixed(f: float, n = 0):
    """
    ## Сокращение цифр после запятой

    ### Входные данные:
    1) Значение, преобразуя его в float
    2) Количество цифр после запятой

    ### Возвращает:
    1) Значение с заданным количеством знаков после запятой
    """
    try:
        a, b = str(f).split('.')
        return '{}.{}{}'.format(a, b[:n], '0'*(n-len(b)))
    except ValueError:
        print("toFixed ValueError: ", f)
        return f


def conversion(currency = None, cost = None):
    """
    ## Конвертер валют

    В качестве аргументов принимаются знак валюты и стоимость

    Всё приводится к значению в долларах
    """
    if currency == '$':
        cost = cost.replace(',','.')
        return toFixed(cost,1)

    if currency == '₽':
        cost = cost.replace(',','.')
        t = ['RUB/USD', cost]
        price = float(cost) / float(parsing.price_value(t))
        return toFixed(price,1)

    if currency == '€':
        cost = cost.replace(',','.')
        t = ['EUR/USD', cost]
        price = float(cost) / float(parsing.price_value(t))
        return toFixed(price,1)