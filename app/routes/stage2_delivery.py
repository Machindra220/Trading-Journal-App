from flask import Blueprint, render_template, request
from sqlalchemy import func
from app.extensions import db
from app.models import Stage2Stock, Stage2DeliveryStock
import yfinance as yf
from datetime import datetime, timedelta
from sqlalchemy import and_

stage2_delivery_bp = Blueprint("stage2_delivery", __name__)

def get_latest_stage2_symbols():
    subquery = db.session.query(
        Stage2Stock.symbol,
        func.max(Stage2Stock.date).label("latest_date")
    ).group_by(Stage2Stock.symbol).subquery()

    latest_entries = db.session.query(Stage2Stock).join(
        subquery,
        (Stage2Stock.symbol == subquery.c.symbol) &
        (Stage2Stock.date == subquery.c.latest_date)
    ).all()

    return latest_entries

def analyze_stage2_stock(symbol, benchmark_hist=None):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="30d")
        if hist.empty or len(hist) < 22:
            return None

        latest = hist.iloc[-1]
        avg_volume = hist["Volume"][:-1].mean()
        delivery_spike = latest["Volume"] / avg_volume
        roc = ((latest["Close"] - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22]) * 100

        if benchmark_hist is None or len(benchmark_hist) < 22:
            return None
        benchmark_roc = ((benchmark_hist["Close"].iloc[-1] - benchmark_hist["Close"].iloc[-22]) / benchmark_hist["Close"].iloc[-22]) * 100
        rs_vs_index = roc - benchmark_roc

        return {
            "symbol": symbol,
            "date": latest.name.date(),
            "price": float(latest["Close"]),
            "volume": int(latest["Volume"]),
            "delivery_spike": round(float(delivery_spike), 2),
            "roc_21d": round(float(roc), 2),
            "rs_vs_index_21d": round(float(rs_vs_index), 2)
        }
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None

@stage2_delivery_bp.route("/stage2-delivery-screener")
def stage2_delivery_screener():
    symbol_filter = request.args.get("symbol", "").upper().strip()
    sort_by = request.args.get("sort", "delivery_spike")
    today = datetime.today().date()

    entries = get_latest_stage2_symbols()
    benchmark_hist = yf.Ticker("^NSEI").history(period="30d")

    results = []
    for entry in entries:
        symbol = entry.symbol
        if symbol_filter and symbol_filter not in symbol:
            continue

        data = analyze_stage2_stock(symbol, benchmark_hist)
        if data and data["delivery_spike"] >= 3:
            tag = (
                "🔥 Strong" if data["delivery_spike"] >= 6 else
                "⚡ Moderate" if data["delivery_spike"] >= 4 else
                "📈 Mild"
            )
            data["tag"] = tag
            data["symbol_clean"] = symbol.replace(".NS", "")
            results.append(data)

            # ✅ Save to DB
            existing = Stage2DeliveryStock.query.filter(
                and_(
                    Stage2DeliveryStock.symbol == symbol,
                    Stage2DeliveryStock.date == today
                )
            ).first()

            if existing:
                updated = False
                for field, new_val in {
                    "price": data["price"],
                    "volume": data["volume"],
                    "delivery_spike": data["delivery_spike"],
                    "roc_21d": data["roc_21d"],
                    "rs_vs_index_21d": data["rs_vs_index_21d"]
                }.items():
                    if getattr(existing, field) != new_val:
                        setattr(existing, field, new_val)
                        updated = True
                if updated:
                    db.session.add(existing)
            else:
                db.session.add(Stage2DeliveryStock(
                    symbol=symbol,
                    date=today,
                    price=data["price"],
                    volume=data["volume"],
                    delivery_spike=data["delivery_spike"],
                    roc_21d=data["roc_21d"],
                    rs_vs_index_21d=data["rs_vs_index_21d"]
                ))

    db.session.commit()

    # ✅ Sorting
    if sort_by == "volume":
        results.sort(key=lambda x: x["volume"], reverse=True)
    elif sort_by == "roc":
        results.sort(key=lambda x: x["roc_21d"], reverse=True)
    elif sort_by == "rs":
        results.sort(key=lambda x: x["rs_vs_index_21d"], reverse=True)
    else:
        results.sort(key=lambda x: x["delivery_spike"], reverse=True)

    return render_template("stage2_delivery_screener.html", stocks=results,
                           sort_by=sort_by, symbol_filter=symbol_filter)

@stage2_delivery_bp.route("/stage2-delivery-history")
def stage2_delivery_history():
    cutoff = datetime.today().date() - timedelta(days=30)
    symbol_filter = request.args.get("symbol", "").upper().strip()

    query = Stage2DeliveryStock.query.filter(Stage2DeliveryStock.date >= cutoff)
    if symbol_filter:
        query = query.filter(Stage2DeliveryStock.symbol.ilike(f"%{symbol_filter}%"))

    stocks = query.order_by(Stage2DeliveryStock.date.desc()).all()

    counts = db.session.query(
        Stage2DeliveryStock.symbol,
        db.func.count(Stage2DeliveryStock.date).label("days_present")
    ).filter(Stage2DeliveryStock.date >= cutoff).group_by(Stage2DeliveryStock.symbol).all()

    presence_map = {symbol: days for symbol, days in counts}

    enriched = []
    for stock in stocks:
        days = presence_map.get(stock.symbol, 0)
        tag = (
            "🔥 30D" if days >= 30 else
            "📆 15D" if days >= 15 else
            "🕒 7D" if days >= 7 else
            "⏳ 3D" if days >= 3 else ""
        )
        enriched.append({
            "date": stock.date,
            "symbol": stock.symbol,
            "symbol_clean": stock.symbol.replace(".NS", ""),
            "price": stock.price,
            "volume": stock.volume,
            "delivery_spike": stock.delivery_spike,
            "roc_21d": stock.roc_21d,
            "rs_vs_index_21d": stock.rs_vs_index_21d,
            "days_present": days,
            "tag": tag
        })

    return render_template("stage2_delivery_history.html", stocks=enriched, symbol_filter=symbol_filter)
