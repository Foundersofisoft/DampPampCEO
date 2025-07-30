import requests
from config import COINGECKO_API_KEY

def get_price(coin_id="cosmos", vs_currency="usd"):
    url = "https://pro-api.coingecko.com/api/v3/simple/price"
    headers = {"x-cg-pro-api-key": COINGECKO_API_KEY}
    params = {"ids": coin_id, "vs_currencies": vs_currency}
    data = requests.get(url, headers=headers, params=params).json()
    return data[coin_id][vs_currency]
