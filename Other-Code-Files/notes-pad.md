Yes Machindra 👌 — you can absolutely integrate **INDmoney API** (and others like DhanHQ, Kite, etc.) into your app. The clean way is to build a **modular extension file** that abstracts API clients. Then your strategy code just calls `DataProvider.get_stock_data("INFY")` without worrying about which API is underneath.

---

## 🔹 Step 1: Create an Extension File
Let’s call it `data_providers.py`. It will contain classes for each API option: **YFinanceProvider**, **INDMoneyProvider**, **DhanHQProvider**.

```python
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
```

---

## 🔹 Step 2: Central Manager
Add a simple manager class to choose which provider to use:

```python
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
```

---

## 🔹 Step 3: Usage in Your Strategy
Now in `rebalance_strategy.py` or anywhere else:

```python
from app.extensions.data_providers import DataProvider

# Choose provider dynamically (env var or config)
provider = DataProvider(provider_name="indmoney")  # or "yfinance", "dhanhq"

stock_data = provider.get_stock_data("INFY")
print(stock_data["current_price"])
```

---

## 🔹 Step 4: Configuration
- Store API keys in `.env`:
  ```
  INDMONEY_API_KEY=your_key_here
  INDMONEY_CLIENT_ID=your_client_id_here
  DHANHQ_ACCESS_TOKEN=your_token_here
  ```
- Load with `python-dotenv` or your config system.

---

## ✅ Benefits
- Clean separation of API logic.  
- Easy to switch providers (just change `provider_name`).  
- Strategy code stays consistent.  
- Supports multiple APIs without duplicating code.

---

👉 Do you want me to also extend this so you can **fall back automatically** (e.g., try INDmoney first, then YFinance if INDmoney fails)? That way your app is resilient if one API is down.