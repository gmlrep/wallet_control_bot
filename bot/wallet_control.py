import asyncio
from pprint import pprint

import aiohttp
from typing import Optional

from bot.db.config import settings


async def get_inf_api(url: str, headers: dict):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as response:
            data = await response.json(encoding='utf8')
            return data


async def get_balance_jettons(wallet_address: str) -> Optional[list]:
    api_key = settings.api_token
    urls = {
        'url': f'https://tonapi.io/v2/accounts/{wallet_address}/jettons?currencies=ton,usd',
        'url_ton': f'https://tonapi.io/v2/accounts/{wallet_address}',
        'url_price_ton': 'https://tonapi.io/v2/rates?tokens=ton&currencies=usd'
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    corut = [get_inf_api(url, headers) for url in urls.values()]
    response = await asyncio.gather(*corut)
    jetton_wallet = response[0]
    ton_wallet = response[1]
    ton_price = response[2]
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


async def check_address(address: str) -> bool:

    url = f'https://tonapi.io/v2/address/{address}/parse'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            status = response.status
            if status != 200:
                return False
            else:
                return True
