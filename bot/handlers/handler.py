import asyncio
import os

import aiohttp
import requests
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from bot.db.requests import create_profile, update_profile_addr, get_address, update_profile_alert, get_list_alert_user
from bot.handlers.keyboard import kb_start, kb_menu, kb_list_addr, kb_settings
from bot.wallet_control import get_balance_jettons, check_address

router = Router()

load_dotenv()


class Address(StatesGroup):
    address = State()


@router.message(Command('start'))
async def start_handler(message: Message):
    is_registered = await create_profile(user_id=message.from_user.id,
                                         user_fullname=message.from_user.full_name,
                                         username=message.from_user.username)
    if is_registered is False:
        await message.answer('Этот бот может отслеживать балансы кошельков и отправлять ежедневные отчеты по балансу. '
                             'Для начала необходимо добавить кошелек для отслеживания', reply_markup=kb_start())
    else:
        await message.answer(text='Главное меню', reply_markup=kb_menu())


@router.callback_query(F.data == 'add_wallet')
async def add_wallet(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Address.address)
    await callback.message.answer(text='Введите адрес кошелька, который хотите отслеживать в сети TON.')
    await callback.answer()


@router.message(F.text, Address.address)
async def set_address(message: Message, state: FSMContext):
    if await check_address(address=message.text):
        data = await get_address(user_id=message.from_user.id)
        addr = f"{data},{message.text}" if data else message.text
        await update_profile_addr(user_id=message.from_user.id, address=addr)
        await message.answer(text='Кошелек успешно добавлен', reply_markup=kb_menu())
        await state.clear()
    else:
        await message.answer(text='Такого адреса не существует. Введите корректный адрес.')


@router.callback_query(F.data == 'list_addr')
async def get_list_addr(callback: CallbackQuery):
    await callback.message.edit_text(text='Выберите нужный адрес',
                                     reply_markup=await kb_list_addr(user_id=callback.from_user.id))
    await callback.answer()


async def get_text_msg(wallet_address: str):
    data = await get_balance_jettons(wallet_address=wallet_address)

    if data is not None:
        text = (
            f"Address - [{wallet_address[:5]}..{wallet_address[len(wallet_address) - 5:len(wallet_address)]}](https://tonscan.org/address/{wallet_address})\n\n"
            f"{round(data[0]['balance'], 2)} 💎 | {round(data[0]['value_usd'], 2)}$\n\n")

        for i in range(1, len(data)):
            text += ''.join(f"⏺ {round(data[i]['balance'], 2)} {data[i]['jetton_name']}\n"
                            f"{round(data[i]['value_ton'], 2)} 💎 | {round(data[i]['value_usd'], 3)}$\n\n")

        total_ton = data[0]['balance']
        for i in range(1, len(data)):
            total_ton += data[i]['value_ton']

        total_usd = 0
        for token in data:
            total_usd += token['value_usd']

        total_dff_24h_usd = 0
        for dff_24h_usd in data:
            total_dff_24h_usd += dff_24h_usd['diff_24h_value']['USD']

        total_diff_24_ton = 0
        for i in range(1, len(data)):
            total_diff_24_ton += data[i]['diff_24h_value']['TON']

        if total_dff_24h_usd >= 0:
            text += ''.join(f"🟢 {round(total_diff_24_ton, 2)} 💎 | +{round(total_dff_24h_usd, 2)}$\n\n")
        else:
            text += ''.join(f"🔴 {round(total_diff_24_ton, 2)} 💎 | {round(total_dff_24h_usd, 2)}$\n\n")

        text += ''.join(f"💰 {round(total_ton, 2)} 💎 | {round(total_usd, 2)}$")
        return text


@router.callback_query(F.data.startswith('show_balance'))
async def show_balance(callback: CallbackQuery):
    wallet_address = callback.data.split(':')[1]
    text = await get_text_msg(wallet_address=wallet_address)
    if text is None:
        await callback.message.answer(text='Что то пошло не так. Попробуйте еще раз.')
    else:
        await callback.message.edit_text(text=text, disable_web_page_preview=True, parse_mode="Markdown")
        await callback.message.answer(text='Главное меню', reply_markup=kb_menu())
    await callback.answer()


@router.callback_query(F.data == 'settings')
async def setting_handlers(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='Настройки',
                                     reply_markup=await kb_settings(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == 'alert')
async def set_alert(callback: CallbackQuery):
    await update_profile_alert(user_id=callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=await kb_settings(user_id=callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data == 'back')
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(text='Главное меню', reply_markup=kb_menu())
    await callback.answer()


async def send_alert_user():
    users = await get_list_alert_user()
    bot_token = os.getenv('BOT_TOKEN')
    for user in users:
        addr_s = await get_address(user_id=user)
        addr_s = addr_s.split(',')

        for addr in addr_s:
            print(user, addr)
            text = await get_text_msg(wallet_address=addr)
            data = {
                "chat_id": f"{user}",
                "parse_mode": "markdown",
                "link_preview_options": {
                    'is_disabled': True
                }
            }
            if text is not None:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage?text={text}"
                response = requests.post(url=url, json=data)
                print(response.json())
            else:
                await asyncio.sleep(1)
                text = await get_text_msg(wallet_address=addr)
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage?text={text}"
                response = requests.post(url=url, json=data)
