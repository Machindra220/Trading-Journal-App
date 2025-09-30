# 📈 Trading Journal

A secure, modular trading journal built with Flask. Track trades, pin resources, export history, and analyze performance.

## 🔧 Features

- ✅ Add/Edit/Delete trades with P&L tracking
- 📌 Pin and manage trading tools
- 📤 Export completed trades to Excel with filters
- 🧠 Filter by stock, date range, and sort by profit
- 🖥️ Compact UI with icon-only actions
- 🕒 Last accessed tracking for resources
- 🕒 Watchlist page
- 🕒 Trades history Page
- 🕒 Notes page 
- 🕒 Simple statistics for our trading performance tracking
- 🖥️ Enhanced trade history view with action buttons (v1.1)

## 🚀 Getting Started Steps

```bash
git clone https://github.com/Machindra220/trading-journal-app.git
cd trading-journal-app
pip install -r requirements.txt
flask run
```
Make sure to add secrets to your .env file.
.env file format as below.

```bash
SECRET_KEY=<your secret key here>
DATABASE_URL=<postgresql://username:password@localhost/db_name>
SQLALCHEMY_TRACK_MODIFICATIONS=False
SQLALCHEMY_ECHO=False
FLASK_ENV=<production / dev >
REMEMBER_COOKIE_SECURE=< True / False >
SESSION_COOKIE_SECURE=< True / False >
```