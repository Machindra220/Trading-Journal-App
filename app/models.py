from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    trades = db.relationship('Trade', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(20), nullable=False)
    entry_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(10), nullable=False, default="Open")  # ✅ Add this line

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    entries = db.relationship('TradeEntry', backref='trade', lazy=True)
    exits = db.relationship('TradeExit', backref='trade', lazy=True)


class TradeEntry(db.Model):
    __tablename__ = 'trade_entries'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)

    # Remove insertable=False — just define the column normally
    # invested_amount = db.Column(db.Float)
    invested_amount = db.Column(db.Numeric, nullable=False, server_default=db.FetchedValue())
    note = db.Column(db.Text)  # ✅ Trade entry Note



class TradeExit(db.Model):
    __tablename__ = 'trade_exits'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    # exit_amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)

    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)
    exit_amount = db.Column(db.Numeric, nullable=False, server_default=db.FetchedValue())
    note = db.Column(db.Text)  # ✅ Trade Exit Note

