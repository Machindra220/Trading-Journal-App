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
    

    events = []
    for trade in trades:
        print(f"Trade: {trade.stock_name}, Exit Date: {trade.exit_date}, PnL: {trade.pnl}")
        print("Entries:", trade.entries)
        print("Exits:", trade.exits)
        if not trade.exit_date:
            continue  # skip if no exit date

        color = '#28a745' if trade.pnl > 0 else '#dc3545' if trade.pnl < 0 else '#ffc107'
        events.append({
            'title': f"{trade.stock_name} ₹{trade.pnl}",
            'start': trade.exit_date.isoformat(),  # ✅ ISO format for FullCalendar
            'color': color,
            'allDay': True,
            'extendedProps': {
                'notes': trade.journal or ''
            }
        })
    print("Emitting events:", events)
  
    return jsonify(events)


@calendar_bp.route('/calendar/summary')
@login_required
def calendar_summary():
    return jsonify(get_pl_summary(current_user.id))

from collections import defaultdict

