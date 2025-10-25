from flask import request, redirect, url_for, Blueprint, render_template, flash
import pandas as pd
import yfinance as yf
import os
from functools import lru_cache
from datetime import datetime, timedelta
# from app.utils.delivery_screener import filter_delivery_surge_stocks




performers_bp = Blueprint("performers", __name__)

@lru_cache(maxsize=128)
def get_1yr_return(symbol, suffix=".NS"):
    try:
        ticker = yf.Ticker(symbol + suffix)
        hist = ticker.history(period="1y", interval="1d")
        if hist.empty or len(hist) < 2:
            return None
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        last_processed_time = datetime.now()  # or from your data pipeline
        return {
            "start_price": round(start_price, 2),
            "end_price": round(end_price, 2),
            "return_pct": round(((end_price - start_price) / start_price) * 100, 2),
            "last_processed_time": last_processed_time 
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def get_top_performers(csv_file, top_n=12, suffix=".NS"):
    if not os.path.exists(csv_file):
        flash(f"CSV file not found: {csv_file}", "error")
        return []

    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip().str.lower()
        results = []

        for symbol in df["symbol"]:
            data = get_1yr_return(symbol, suffix)
            if data:
                results.append({
                    "symbol": symbol,
                    "start_price": data["start_price"],
                    "end_price": data["end_price"],
                    "return_pct": data["return_pct"]
                })

        top_df = pd.DataFrame(results).sort_values(by="return_pct", ascending=False).head(top_n)
        top_df.reset_index(drop=True, inplace=True)
        top_df["rank"] = top_df.index + 1
        return top_df.to_dict(orient="records")
    except Exception as e:
        flash(f"Error processing {csv_file}: {e}", "error")
        return []

@performers_bp.route("/top-performers")
def top_performers():
    nifty_200 = get_top_performers("data/nifty_200.csv", top_n=20, suffix=".NS")
    nifty_500 = get_top_performers("data/nifty_500.csv", top_n=20, suffix=".NS")
    bse_200 = get_top_performers("data/bse_200.csv", top_n=20, suffix=".BO")

    n200_set = set([s["symbol"] for s in nifty_200])
    n500_set = set([s["symbol"] for s in nifty_500])
    bse_set = set([s["symbol"] for s in bse_200])
    # overlaps = n200_set & n500_set & bse_set
    
    overlap_n200_bse = n200_set & bse_set
    overlap_n200_n500 = n200_set & n500_set
    overlap_bse_n500 = bse_set & n500_set
    overlap_all = n200_set & bse_set & n500_set
    last_processed_time = datetime.now()

    return render_template("top_performers.html",
                           nifty_200=nifty_200,
                           nifty_500=nifty_500,
                           bse_200=bse_200,
                           overlap_n200_bse=overlap_n200_bse,
                           overlap_n200_n500=overlap_n200_n500,
                           overlap_bse_n500=overlap_bse_n500,
                           overlap_all=overlap_all,
                           last_processed_time=last_processed_time)

@performers_bp.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files.get("csv_file")
    if not file or not file.filename.endswith(".csv"):
        flash("Please upload a valid CSV file.", "error")
        return redirect(url_for("performers.top_performers"))

    save_path = os.path.join("data", file.filename)
    file.save(save_path)
    flash(f"Uploaded {file.filename} successfully.", "info")
    return redirect(url_for("performers.top_performers"))

# delivery_surge screener code
# app/utils/delivery_screener.py

def load_nifty500_tickers():
    df = pd.read_csv("data/nifty_500.csv")
    df.columns = df.columns.str.strip().str.lower()
    return [s + ".NS" for s in df["symbol"].dropna().unique()]

def analyze_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        market_cap = info.get("marketCap", 0)
        if market_cap < 100 * 10**7:
            return None

        hist = stock.history(period="15d")
        if hist.empty or len(hist) < 5:
            return None

        latest = hist.iloc[-1]
        avg_volume = hist["Volume"][:-1].mean()
        delivery_spike = latest["Volume"] / avg_volume

        return {
            "ticker": ticker,
            "current_price": latest["Close"],
            "price_change": latest["Close"] - latest["Open"],
            "price_change_pct": round((latest["Close"] - latest["Open"]) / latest["Open"] * 100, 2),
            "volume": int(latest["Volume"]),
            "delivery_spike": round(delivery_spike, 2),
            "market_cap": market_cap
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

def filter_delivery_surge_stocks():
    tickers = load_nifty500_tickers()
    results = []
    for ticker in tickers:
        data = analyze_stock(ticker)
        if not data:
            continue
        if (
            data["price_change"] > 0 and
            data["volume"] > 20000 and
            data["delivery_spike"] >= 4
        ):
            results.append(data)
    results.sort(key=lambda x: x["delivery_spike"], reverse=True)
    return results

# app/routes/performers.py

delivery_bp = Blueprint("delivery", __name__)

@delivery_bp.route("/delivery-surge")
def delivery_surge():
    stocks = filter_delivery_surge_stocks()
    last_processed_time = datetime.now()
    return render_template("delivery_surge.html", stocks=stocks, last_processed_time=last_processed_time)
