from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import Trade
from app.utils import get_pl_summary  # helper for aggregated stats

calendar_bp = Blueprint('calendar', __name__)

@calendar_bp.route('/calendar')
@login_required
def calendar_view():
    return render_template('calendar.html')

#calendar events route
@calendar_bp.route('/calendar/events')
@login_required
def calendar_events():
    trades = Trade.query.filter_by(user_id=current_user.id, status='closed').all()
    daily = defaultdict(list)

    for trade in trades:
        key = str(trade.exit_date)
        daily[key].append(trade)

    events = []
    for day, trades in daily.items():
        total = sum(t.pnl for t in trades)
        color = '#28a745' if total > 0 else '#dc3545' if total < 0 else '#ffc107'
        tooltip = '\n'.join([f"{t.stock_name}: ₹{t.pnl} — {t.journal or ''}" for t in trades])
        events.append({
            'title': f"₹{round(total, 2)}",
            'start': day,
            'color': color,
            'allDay': True,  # ✅ This ensures proper rendering in dayGridMonth
            'extendedProps': {
                'notes': tooltip
            }
        })
    return jsonify(events)

@calendar_bp.route('/calendar/summary')
@login_required
def calendar_summary():
    return jsonify(get_pl_summary(current_user.id))

from collections import defaultdict

