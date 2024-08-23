import asyncio
import json

from bs4 import BeautifulSoup
from fake_headers import Headers
import aiohttp


async def prepare_data(jetton_wallet, ton_wallet, ton_price):
    try:
        balance_ton = int(ton_wallet['balance']) / 1000000000
        price_ton = ton_price['rates']['TON']['prices']['USD']
        value_usd = balance_ton * price_ton
        diff_24h_usd = ton_price['rates']['TON']['diff_24h']['USD'].split('%')[0]
        diff_24h_usd = float(diff_24h_usd.replace('−', '-'))

        native = {
            'jetton_name': 'TON',
            'balance': balance_ton,
            'price_ton': price_ton,
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

                    value_ton = balance * (resp['price']['prices']['TON'])
                    value_usd = balance * price_usd

                    jettons.append({
                        'jetton_name': resp['jetton']['symbol'],
                        'balance': balance,

                        'value_ton': value_ton,
                        'value_usd': value_usd,
                        'diff_24h_value': {
                            'TON': value_ton * diff_24h_ton / 100,
                            'USD': value_usd * diff_24h_usd / 100
                        }
                    })
        jettons.sort(key=lambda x: x['value_usd'], reverse=True)

        return {'native': native, 'jettons': jettons}
    except KeyError:
        return None


class TonApi:

    def __init__(
            self,
            api_key: str
    ):

        self.api_key = api_key

    async def balance_jettons(
            self,
            wallet_address: str
    ) -> dict | None:

        """
        Balance of ton and jettons from TON for wallet address

        :param wallet_address: address of wallet on ton blockchain
        :return: balance ton and jetton :class:`dict`
        """

        urls = {
            'url': f'https://tonapi.io/v2/accounts/{wallet_address}/jettons?currencies=ton,usd',
            'url_ton': f'https://tonapi.io/v2/accounts/{wallet_address}',
            'url_price_ton': 'https://tonapi.io/v2/rates?tokens=ton&currencies=usd'
        }

        to_do = [self._get_response(url) for url in urls.values()]
        jetton_wallet, ton_wallet, ton_price = list(await asyncio.gather(*to_do))

        if not jetton_wallet or not ton_wallet or not ton_price:
            return

        jettons = await prepare_data(jetton_wallet, ton_wallet, ton_price)

        if not jettons:
            return

        nft, qt_nft = await self._nft_balance(addr=wallet_address)
        if nft != 0 or not nft:
            nft = {'ton': nft, 'usdt': nft * jettons['native']['price_ton'], 'quantity': qt_nft}
        else:
            nft = None
        jettons['nft'] = nft
        return jettons

    async def check_address(
            self,
            address: str
    ) -> bool | None:

        url = f'https://tonapi.io/v2/address/{address}/parse'
        if await self._get_response(url, response_type='status_code'):
            return True
        return

    async def _get_response(
            self,
            url: str,
            headers: dict | None = None,
            params: dict | None = None,
            response_type: str = 'json'
    ) -> dict | str | bool | None:

        if not headers:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, params=params) as response:
                if response.status != 200:
                    return
                if response_type == 'json':
                    return await response.json(encoding='utf-8')
                if response_type == 'text':
                    return await response.text()
                if response_type == 'status_code':
                    return True
                # raise

    async def _nfts_info(
            self,
            addr: str
    ):

        url = f'https://tonapi.io/v2/accounts/{addr}/nfts'
        params = {
            'limit': 1000,
            'offset': 0,
            'indirect_ownership': 'true'
        }
        data = await self._get_response(url=url, params=params)

        nft_list = []

        try:
            for nft in data['nft_items']:
                if nft['trust'] not in ['blacklist'] and nft['approved_by'] == ['getgems']:
                    nft_list.append(nft['collection']['address'])
            return nft_list

        except KeyError:
            return

    async def _nft_floor_price(
            self,
            addr: str
    ) -> float | None:

        url = f'https://getgems.io/collection/{addr}'
        headers = Headers(browser="chrome", os="win", headers=True)

        html_index = await self._get_response(url=url, headers=headers.generate(), response_type='text')

        data = BeautifulSoup(html_index, 'html.parser')
        props = data.find(id='__NEXT_DATA__').text
        props = json.loads(props)

        try:
            props = props['props']['pageProps']['gqlCache']['ROOT_QUERY']
            props = props['alphaNftCollectionStats({"address":"' + addr + '"})']['floorPrice']
        except KeyError:
            return

        try:
            props = float(props)
        except ValueError:
            return
        return props

    async def _nft_balance(
            self,
            addr: str
    ):

        nfts = await self._nfts_info(addr=addr)

        if not nfts:
            return

        cor = []
        for nft in nfts:
            cor.append(self._nft_floor_price(addr=nft))
        prices = await asyncio.gather(*cor)
        return sum(prices), len(nfts)
