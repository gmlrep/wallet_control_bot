import asyncio
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import aiohttp

from bot.db.config import settings


async def get_response(session: aiohttp.ClientSession, url: str, headers: dict) -> dict | None:
    async with session.get(url=url, headers=headers) as response:
        if response.status != 200:
            return
        data = await response.json(encoding='utf8')
        return data


async def get_inf_api(urls: dict, headers: dict):
    async with aiohttp.ClientSession() as session:
        to_do = [get_response(session, url, headers) for url in urls.values()]
        return await asyncio.gather(*to_do)


async def get_balance_jettons(wallet_address: str) -> dict | None:
    """
    Balance of ton and jettons from TON for wallet address

    :param wallet_address: address of wallet on ton blockchain
    :return: balance ton and jetton :class:`dict`
    """

    api_key = settings.api_token
    urls = {
        'url': f'https://tonapi.io/v2/accounts/{wallet_address}/jettons?currencies=ton,usd',
        'url_ton': f'https://tonapi.io/v2/accounts/{wallet_address}',
        'url_price_ton': 'https://tonapi.io/v2/rates?tokens=ton&currencies=usd'
    }
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    jetton_wallet, ton_wallet, ton_price = list(await get_inf_api(urls=urls, headers=headers))

    if not jetton_wallet or not ton_wallet or not ton_price:
        return

    balance_ton = int(ton_wallet['balance']) / 1000000000
    price_ton = ton_price['rates']['TON']['prices']['USD']

    try:
        value_usd = balance_ton * price_ton
        diff_24h_usd = ton_price['rates']['TON']['diff_24h']['USD'].split('%')[0]
        diff_24h_usd = float(diff_24h_usd.replace('−', '-'))

        native = {
            'jetton_name': 'TON',
            'balance': balance_ton,
            'price_usd': price_ton,
            'value_usd': value_usd,
            'diff_24h_value': {
                'USD': value_usd * diff_24h_usd / 100
            }
        }
        jettons = []
        for resp in jetton_wallet['balances']:
            if (bal := int(resp['balance'])) != 0:
                balance = bal / 10 ** int(resp['jetton']['decimals'])
                value = balance * (price_usd := resp['price']['prices']['USD'])

                if value > 0.1:
                    diff_24h_ton = resp['price']['diff_24h']['TON'].split('%')[0]
                    diff_24h_usd = resp['price']['diff_24h']['USD'].split('%')[0]
                    diff_24h_ton = float(diff_24h_ton.replace('−', '-'))
                    diff_24h_usd = float(diff_24h_usd.replace('−', '-'))

                    value_ton = balance * (price_ton := resp['price']['prices']['TON'])
                    value_usd = balance * price_usd

                    jettons.append({
                        'jetton_name': resp['jetton']['symbol'],
                        'balance': balance,
                        'price_ton': price_ton,
                        'price_usd': price_usd,
                        'value_ton': value_ton,
                        'value_usd': value_usd,
                        'diff_24h_value': {
                            'TON': value_ton * diff_24h_ton / 100,
                            'USD': value_usd * diff_24h_usd / 100
                        }
                    })
        jettons.sort(key=lambda x: x['value_usd'], reverse=True)
        nft = get_nft_balance(addr=wallet_address)
        if nft != 0:
            nft = {'ton': nft, 'usdt': nft * price_ton * 10000}
        else:
            nft = None
        return {'native': native, 'jettons': jettons, 'nft': nft}
    except KeyError:
        return


async def check_address(address: str) -> bool | None:
    url = f'https://tonapi.io/v2/address/{address}/parse'

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            status = response.status
            if status != 200:
                return
            return True


def get_nfts_from_acc(addr: str):
    url = f'https://tonapi.io/v2/accounts/{addr}/nfts'
    param = {
        'limit': 1000,
        'offset': 0
    }

    data = requests.get(url=url, params=param)
    data = data.json()
    data = data['nft_items']
    nft_list = []
    for nft in data:
        if nft['trust'] not in ['blacklist'] and nft['approved_by'] == ['getgems']:
            nft_list.append(nft['collection']['address'])
    return nft_list


def get_nft_floor_price(addr: str) -> float | None:

    url = f'https://getgems.io/collection/{addr}'
    headers = Headers(browser="chrome", os="win", headers=True)
    html_index = requests.get(url=url, headers=headers.generate())

    data = BeautifulSoup(html_index.text, 'html.parser')
    props = data.find(id='__NEXT_DATA__').text
    props = json.loads(props)
    props = props['props']['pageProps']['gqlCache']['ROOT_QUERY']['alphaNftCollectionStats({"address":"' + addr + '"})']['floorPrice']

    try:
        props = float(props)
    except ValueError:
        return
    return props


def get_nft_balance(addr: str):
    nfts = get_nfts_from_acc(addr=addr)
    sum = 0
    for nft in nfts:
        sum += get_nft_floor_price(addr=nft)
    return sum


# print(get_nft_balance(addr='UQCq_TkDcTyDJFDQSNoKljOXdejDKV-s-WIXi0xGHBeciiRo'))