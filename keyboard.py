from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton
from telebot import types

tick_butt = types.KeyboardButton('Тикер')
menu_butt = types.KeyboardButton('Портфель')

menu_stock_add = types.InlineKeyboardButton(text = 'Добавить', callback_data = 'add')
menu_stock_edit = types.InlineKeyboardButton(text = 'Изменить', callback_data = 'edit')
menu_stock_cost = types.InlineKeyboardButton(text = 'Узнать цену', callback_data = 'cost')

cancel_butt = types.InlineKeyboardButton(text = 'Отмена', callback_data = 'cancel')

def keyboard_down():
    """
    ## Постоянная клавиатура (снизу)

    Имеет две кнопки:
    1) Тикер
    2) Портфель
    """
    down_kb = types.ReplyKeyboardMarkup(
        row_width = 1,
        resize_keyboard = True,
        one_time_keyboard = True
        ).add(tick_butt,menu_butt)

    return down_kb

def menu_stock():
    """
    ## Клавиатура привязанная к сообщению о портфеле
    """
    inLineKeybord = types.InlineKeyboardMarkup(row_width = 2)
    inLineKeybord.add(menu_stock_add,menu_stock_edit,menu_stock_cost)

    return inLineKeybord

def cancel_menu():
    """
    ## Клавиатура с кнопкой отмены, привязанная к сообщению
    """
    inLineKeybord = types.InlineKeyboardMarkup()
    inLineKeybord.add(cancel_butt)
    return inLineKeybord