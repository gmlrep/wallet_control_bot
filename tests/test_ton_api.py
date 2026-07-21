import pytest

from bot.utils.ton_api import prepare_data


@pytest.mark.asyncio
async def test_prepare_data_builds_native_and_sorted_jettons():
    jetton_wallet = {
        "balances": [
            {
                "balance": "2500000000",
                "jetton": {"decimals": "9", "symbol": "AAA"},
                "price": {
                    "prices": {"USD": 2.0, "TON": 0.5},
                    "diff_24h": {"USD": "10%", "TON": "5%"},
                },
            },
            {
                "balance": "100000000",
                "jetton": {"decimals": "8", "symbol": "SMALL"},
                "price": {
                    "prices": {"USD": 0.05, "TON": 0.01},
                    "diff_24h": {"USD": "1%", "TON": "1%"},
                },
            },
            {
                "balance": "1000000000",
                "jetton": {"decimals": "9", "symbol": "BBB"},
                "price": {
                    "prices": {"USD": 1.0, "TON": 0.2},
                    "diff_24h": {"USD": "−2.5%", "TON": "−1.5%"},
                },
            },
        ]
    }
    ton_wallet = {"balance": "5000000000"}
    ton_price = {
        "rates": {
            "TON": {
                "prices": {"USD": 6.0},
                "diff_24h": {"USD": "12.5%"},
            }
        }
    }

    result = await prepare_data(jetton_wallet, ton_wallet, ton_price)

    assert result["native"] == {
        "jetton_name": "TON",
        "balance": 5.0,
        "price_ton": 6.0,
        "value_usd": 30.0,
        "diff_24h_value": {"USD": 3.75},
    }
    assert [item["jetton_name"] for item in result["jettons"]] == ["AAA", "BBB"]
    assert result["jettons"][0]["value_usd"] == 5.0
    assert result["jettons"][0]["diff_24h_value"]["TON"] == pytest.approx(0.0625)
    assert result["jettons"][0]["diff_24h_value"]["USD"] == pytest.approx(0.5)
    assert result["jettons"][1]["diff_24h_value"]["TON"] == pytest.approx(-0.003)
    assert result["jettons"][1]["diff_24h_value"]["USD"] == pytest.approx(-0.025)


@pytest.mark.asyncio
async def test_prepare_data_returns_none_for_missing_keys():
    result = await prepare_data({}, {}, {})

    assert result is None
