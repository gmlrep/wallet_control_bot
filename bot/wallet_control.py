import asyncio
import os
import time
from datetime import datetime
from pprint import pprint

import aiohttp
import requests

from bot.db.config import settings


async def get_balance_jeton(wallet_address: str):
    api_key = settings.api_token

    url = f'https://tonapi.io/v2/accounts/{wallet_address}/jettons?currencies=ton,usd'
    url_ton = f'https://tonapi.io/v2/accounts/{wallet_address}'
    url_price_ton = 'https://tonapi.io/v2/rates?tokens=ton&currencies=usd'

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            jetton_wallet = await response.json(encoding='utf8')
            await asyncio.sleep(.7)
        async with session.get(url=url_ton, headers=headers) as response:
            ton_wallet = await response.json(encoding='utf8')
            await asyncio.sleep(.7)
        async with session.get(url=url_price_ton, headers=headers) as response:
            ton_price = await response.json(encoding='utf8')
            await asyncio.sleep(.7)
    try:
        value_usd = int(ton_wallet['balance']) / 1000000000 * ton_price['rates']['TON']['prices']['USD']
        diff_24h_usd = ton_price['rates']['TON']['diff_24h']['USD'].split('%')[0]
        diff_24h_usd = float(diff_24h_usd.replace('−', '-'))

        list_jetton = [{
            'jetton_name': 'TON',
            'balance': int(ton_wallet['balance']) / 1000000000,
            'price_usd': ton_price['rates']['TON']['prices']['USD'],
            'value_usd': value_usd,
            'diff_24h': {
                'USD': ton_price['rates']['TON']['diff_24h']['USD']
            },
            'diff_24h_value': {
                'USD': value_usd * diff_24h_usd / 100
            }
        }]
        for resp in jetton_wallet['balances']:
            if int(resp['balance']) != 0:
                balance = int(resp['balance']) / 10**int(resp['jetton']['decimals'])
                value = balance * resp['price']['prices']['USD']
                if value > 0.1:
                    diff_24h_ton = resp['price']['diff_24h']['TON'].split('%')[0]
                    diff_24h_usd = resp['price']['diff_24h']['USD'].split('%')[0]
                    diff_24h_ton = float(diff_24h_ton.replace('−', '-'))
                    diff_24h_usd = float(diff_24h_usd.replace('−', '-'))

                    value_ton = balance * resp['price']['prices']['TON']
                    value_usd = balance * resp['price']['prices']['USD']

                    list_jetton.append({
                        'jetton_name': resp['jetton']['symbol'],
                        'balance': balance,
                        'price_ton': resp['price']['prices']['TON'],
                        'price_usd': resp['price']['prices']['USD'],
                        'value_ton': value_ton,
                        'value_usd': value_usd,
                        'diff_24h': {
                            'TON': resp['price']['diff_24h']['TON'],
                            'USD': resp['price']['diff_24h']['USD']
                        },
                        'diff_24h_value': {
                            'TON': value_ton * diff_24h_ton / 100,
                            'USD': value_usd * diff_24h_usd / 100
                        }
                    })
        return list_jetton
    except KeyError:
        pass


async def check_address(address: str):

    url = f'https://tonapi.io/v2/address/{address}/parse'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            status = await response.json()
            try:
                error_status = status['error']
                return False
            except KeyError:
                return True



# from pytonapi import Tonapi
# from pytonapi.utils import nano_to_amount


# API_KEY = os.getenv('API_KEY')
ACCOUNT_ID = "UQCq_TkDcTyDJFDQSNoKljOXdejDKV-s-WIXi0xGHBeciiRo"
JETON_ID = 'EQD3U8yc2moTe8yCbUlYxkMh_SCCWLkuxQam2lab4iDfpXYU'


# def mnm():
#     tonapi = Tonapi(api_key=API_KEY)
#     result = tonapi.blockchain.get_account_transactions(account_id=ACCOUNT_ID, limit=1000)
#     rep = tonapi.blockchain.get_account_info(account_id='EQDa4VOnTYlLvDJ0gZjNYm5PXfSmmtL6Vs6A_CZEtXCNICq_')
#     # print(rep.address)
#
#     for transaction in result.transactions:
#         try:
#             if transaction.out_msgs[0].decoded_op_name == 'dedust_swap':
#                 print(transaction)
#                 print(nano_to_amount(transaction.out_msgs[0].value))
#         except:
#             pass
#
#
# mnm()

def mnmn():
    url1 = f'https://tonapi.io/v2/accounts/{ACCOUNT_ID}/jettons/history'
    url = f'https://tonapi.io/v2/accounts/{ACCOUNT_ID}/jettons/{JETON_ID}/history'
    params = {
        'limit': 100,
        'start_date': 1668436763,
        'end_date': int(datetime.now().timestamp()),
    }
    resp = requests.get(url=url, params=params)
    pprint(resp.json())
    # dict_jet = {
    #     'status':
    # }


# mnmn()
