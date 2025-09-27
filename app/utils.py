from datetime import date, timedelta
from app.models import Trade
# from app.extensions import db

def get_pl_summary(user_id):
    today = date.today()
    start_month = today.replace(day=1)
    start_3m = today - timedelta(days=90)
    start_q = today.replace(month=((today.month - 1)//3)*3 + 1, day=1)
    start_year = today.replace(month=1, day=1)

    def sum_pl(start):
        trades = Trade.query.filter(
            Trade.user_id == user_id,
            Trade.status.ilike('closed'),
            Trade.exit_date >= start
        ).all()
        return sum(t.pnl for t in trades)

    return {
        'this_month': round(sum_pl(start_month), 2),
        'last_3_months': round(sum_pl(start_3m), 2),
        'quarter': round(sum_pl(start_q), 2),
        'year': round(sum_pl(start_year), 2)
    }
