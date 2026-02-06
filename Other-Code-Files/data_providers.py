# app/extensions/data_providers.py

import yfinance as yf
import requests
import os

class YFinanceProvider:
    def get_stock_data(self, symbol: str):
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")
        return {
            "symbol": symbol,
            "current_price": float(hist["Close"].iloc[-1]),
            "history": hist
        }


class INDMoneyProvider:
    BASE_URL = "https://api.indstocks.com/v1"
    
    def __init__(self, api_key: str, client_id: str):
        self.api_key = api_key
        self.client_id = client_id

    def get_stock_data(self, symbol: str):
        url = f"{self.BASE_URL}/stock/{symbol}"
        headers = {
            "x-api-key": self.api_key,
            "x-client-id": self.client_id
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return {
            "symbol": symbol,
            "current_price": float(data["price"]),
            "history": data.get("history", [])
        }


class DhanHQProvider:
    BASE_URL = "https://api.dhan.co/v1"
    
    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_stock_data(self, symbol: str):
        url = f"{self.BASE_URL}/marketdata/{symbol}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return {
            "symbol": symbol,
            "current_price": float(data["last_price"]),
            "history": data.get("ohlc", [])
        }

class DataProvider:
    def __init__(self, provider_name="yfinance"):
        if provider_name == "yfinance":
            self.provider = YFinanceProvider()
        elif provider_name == "indmoney":
            self.provider = INDMoneyProvider(
                api_key=os.getenv("INDMONEY_API_KEY"),
                client_id=os.getenv("INDMONEY_CLIENT_ID")
            )
        elif provider_name == "dhanhq":
            self.provider = DhanHQProvider(
                access_token=os.getenv("DHANHQ_ACCESS_TOKEN")
            )
        else:
            raise ValueError(f"Unknown provider: {provider_name}")

    def get_stock_data(self, symbol: str):
        return self.provider.get_stock_data(symbol)
