import os
import requests
import finnhub

from django.shortcuts import render, redirect

def lookup(symbol):
    """Look up quote for symbol."""
    finnhub_client = finnhub.Client(api_key="c8qsmt2ad3ienapjspgg")

    # Parse response
    try:
        quote = finnhub_client.quote(symbol)
        info = finnhub_client.company_profile2(symbol=f'{symbol}')
        return {
            "name": info["name"],
            "exchange": info["exchange"],
            "logo": info["logo"],
            "web" : info["weburl"],
            "currency":info["currency"],
            "country":info["country"],
            "price": float(quote["c"]),
            "symbol": info["ticker"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def lookupcrypto(coin, coin_to):
    """Look up quote for symbol."""
    # Contact API
    try:
        url = f"https://min-api.cryptocompare.com/data/all/coinlist?api_key='47029130d507a80efe847e4d84328f8526810328ef36172acd6d934625a2d5d9'"
        url2 = f'https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms={coin_to}&api_key=47029130d507a80efe847e4d84328f8526810328ef36172acd6d934625a2d5d9'
        response = requests.get(url)
        r2 = requests.get(url2)
        r2.raise_for_status()
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = r2.json()
        d1 = response.json()
        n = d1['Data'][f'{coin}']["FullName"]
        return {
            "exchange": quote[f'{coin_to}'],
            "name": n[0: n.index("(")],
            "description": d1["Data"][f"{coin}"]["Description"]

        }
    except (KeyError, TypeError, ValueError):
        return None

# For looking up the coin for buying or selling this function returns only necessary information.
def lookupcryptobs(coin):
    # Contact API
    try:
        url = f"https://min-api.cryptocompare.com/data/all/coinlist?fsym={coin}"
        url2 = f'https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD'
        response = requests.get(url2)
        r1 = requests.get(url)
        r1.raise_for_status()
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        d1 = r1.json()
        n = d1['Data'][f'{coin}']["FullName"]
        return {
            "price": quote["USD"],
            "name": n[0: n.index("(")],
        }
    except (KeyError, TypeError, ValueError):
        return None

def lookupcurrency(coin, coin_to):
    try:
        url = f'https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms={coin_to}&api_key=47029130d507a80efe847e4d84328f8526810328ef36172acd6d934625a2d5d9'
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        quote = response.json()
        return {
            'price': quote[f'{coin_to}']
        }
    except (KeyError, TypeError, ValueError):
        return None


def news(stock):
    try:
        url = f"https://newsapi.org/v2/everything?q={stock}&apiKey=b779ac65a31c493498ae07e7c767a25a"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    data = response.json()
    data = data["articles"]
    data = data[:5]
    return data


