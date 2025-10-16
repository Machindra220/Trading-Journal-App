from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Trade
from app.utils import get_pl_summary
from collections import defaultdict
from datetime import datetime

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def calendar_view():
    today = datetime.today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))
    return render_template("calendar.html", month=month, year=year)

@calendar_bp.route('/calendar/events')
@login_required
def calendar_events():
    trades = Trade.query.filter_by(user_id=current_user.id, status='closed').all()
    daily_pnl = defaultdict(float)

    for trade in trades:
        if trade.exit_date:
            date_str = trade.exit_date.strftime("%Y-%m-%d")
            daily_pnl[date_str] += trade.pnl

    return jsonify(daily_pnl)

@calendar_bp.route('/calendar/summary')
@login_required
def calendar_summary():
    return jsonify(get_pl_summary(current_user.id))
