from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.requests import get_address, get_alert_status, get_addr_name


def kb_start():
    start = InlineKeyboardBuilder()
    start.button(text='Добавить кошелек', callback_data='add_wallet')
    start.adjust(1)
    return start.as_markup()


def kb_menu():
    menu = InlineKeyboardBuilder()
    menu.button(text='Показать баланс', callback_data='list_addr')
    menu.button(text='Быстрый просмотр баланса', callback_data='single_view_balance')
    menu.button(text='Добавить кошелек', callback_data='add_wallet')
    menu.button(text='Настройки', callback_data='settings')
    menu.adjust(1)
    return menu.as_markup()


async def kb_list_addr(user_id: int):
    address = await get_addr_name(user_id=user_id)
    addr_btn = InlineKeyboardBuilder()
    for addr in address:
        if addr[1]:
            addr_btn.button(text=addr[1], callback_data=f'show_balance:{addr[0]}')
        else:
            addr_btn.button(text=f"{addr[0][:5]}..{addr[0][len(addr[0])-5:len(addr[0])]}",
                            callback_data=f'show_balance:{addr[0]}')

    addr_btn.button(text='Редактировать', callback_data='edit_addr_list')
    addr_btn.button(text="Назад", callback_data='back')
    addr_btn.adjust(1)
    return addr_btn.as_markup()


async def kb_list_edit_delete(user_id: int):
    address = await get_addr_name(user_id=user_id)
    addr_btn = InlineKeyboardBuilder()
    for addr in address:
        if addr[1]:
            addr_btn.button(text=addr[1], callback_data=f'show_balance:{addr[0]}')
        else:
            addr_btn.button(text=f"{addr[0][:5]}..{addr[0][len(addr[0])-5:len(addr[0])]}",
                            callback_data=f'show_balance:{addr[0]}')

        addr_btn.button(text='✏️', callback_data=f'edit_address:{addr[0]}')
        addr_btn.button(text='❌', callback_data=f'delete_address:{addr[0]}')
    addr_btn.button(text="Назад", callback_data='back')
    addr_btn.adjust(3)
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
