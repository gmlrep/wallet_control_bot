import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.requests import get_address, get_alert_status


def kb_start():
    start = InlineKeyboardBuilder()
    start.button(text='Добавить кошелек', callback_data='add_wallet')
    start.adjust(1)
    return start.as_markup()


def kb_menu():
    menu = InlineKeyboardBuilder()
    menu.button(text='Показать баланс', callback_data='list_addr')
    menu.button(text='Добавить кошелек', callback_data='add_wallet')
    menu.button(text='Настройки', callback_data='settings')
    menu.adjust(1)
    return menu.as_markup()


async def kb_list_addr(user_id: int):
    data = await get_address(user_id=user_id)
    addr_btn = InlineKeyboardBuilder()
    list_addr = data.split(',')
    for addr in list_addr:
        addr_btn.button(text=f"{addr[:5]}..{addr[len(addr)-5:len(addr)]}", callback_data=f'show_balance:{addr}')
    addr_btn.button(text="Назад", callback_data='back')
    addr_btn.adjust(1, 1, 1, 1, 1, 1, 1)
    return addr_btn.as_markup()


async def kb_settings(user_id: int):
    settings = InlineKeyboardBuilder()
    data = await get_alert_status(user_id=user_id)
    if data:
        settings.button(text="✅ Отчет", callback_data='alert')
    else:
        settings.button(text="❌ Отчет", callback_data='alert')
    settings.button(text="Назад", callback_data='back')
    settings.adjust(1, 1)
    return settings.as_markup()


async def mai():
    data = await get_alert_status(user_id=312390617)
    print(data)

# asyncio.run(mai())
