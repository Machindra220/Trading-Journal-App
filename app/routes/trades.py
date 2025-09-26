from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.models import Trade, TradeEntry, TradeExit
from app import db
from datetime import date, timedelta
import pandas as pd
from io import BytesIO




trades_bp = Blueprint('trades', __name__)

# Dashboard Route
@trades_bp.route('/dashboard')
@login_required
def dashboard():
    trades = Trade.query.filter_by(user_id=current_user.id).all()

    trade_data = []
    for trade in trades:
        total_invested = sum(e.invested_amount for e in trade.entries)
        total_exited = sum(e.exit_amount for e in trade.exits)

        # Use status from DB directly
        status = trade.status

        # Only calculate P&L if trade is closed
        pnl = total_exited - total_invested if status == "Closed" else None

        trade_data.append({
            'id': trade.id,
            'stock_name': trade.stock_name,
            'status': status,
            'total_invested': float(total_invested),
            'total_exited': float(total_exited),
            'pnl': float(pnl) if pnl is not None else None
        })

    return render_template('dashboard.html', trades=trade_data)



#Backend Route: add_trade
@trades_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_trade():
    if request.method == 'POST':
        stock_name = request.form.get('stock_name', '').strip().upper()
        entry_note = request.form.get('entry_note', '').strip()

        if not stock_name:
            flash("Stock name is required.", "error")
            return redirect(url_for('trades.add_trade'))

        try:
            new_trade = Trade(stock_name=stock_name, entry_note=entry_note, user_id=current_user.id)
            db.session.add(new_trade)
            db.session.commit()
            flash(f"Trade for {stock_name} created successfully.", "success")
            return redirect(url_for('trades.view_trade', trade_id=new_trade.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error creating trade: {str(e)}", "error")
            return redirect(url_for('trades.add_trade'))

    return render_template('add_trade.html')



# View Trades Route
@trades_bp.route('/trade/<int:trade_id>')
@login_required
def view_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    entries = TradeEntry.query.filter_by(trade_id=trade.id).order_by(TradeEntry.date).all()
    exits = TradeExit.query.filter_by(trade_id=trade.id).order_by(TradeExit.date).all()

    total_invested = sum(e.invested_amount for e in entries)
    total_exited = sum(x.exit_amount for x in exits)
    total_buy_qty = sum(e.quantity for e in entries)
    total_sell_qty = sum(x.quantity for x in exits)

    status = "Closed" if total_buy_qty == total_sell_qty else "Open"
    pnl = total_exited - total_invested if status == "Closed" else None

    # Duration logic
    if entries:
        start_date = entries[0].date
        end_date = exits[-1].date if status == "Closed" and exits else date.today()
        duration_days = (end_date - start_date).days
    else:
        duration_days = 0

    return render_template(
        'view_trade.html',
        trade=trade,
        entries=entries,
        exits=exits,
        status=status,
        pnl=round(pnl, 2) if pnl is not None else None,
        duration_days=duration_days
    )


# add_entry – Log a Buy
@trades_bp.route('/trade/<int:trade_id>/entry', methods=['POST'])
@login_required
def add_entry(trade_id):
    trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    try:
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        date_str = request.form['date']
        date_obj = date.fromisoformat(date_str)
        note = request.form.get('note', '').strip()

        # ✅ Check current trade state
        total_buy_qty = sum(e.quantity for e in trade.entries)
        total_sell_qty = sum(x.quantity for x in trade.exits)

        # ❌ Prevent buy if trade is already closed
        if total_buy_qty == total_sell_qty and total_buy_qty > 0:
            flash("Trade is closed. Start a new trade to buy again.", "error")
            return redirect(url_for('trades.view_trade', trade_id=trade.id))

        # ❌ Prevent buy if sell quantity already exceeds buy quantity
        if total_sell_qty > total_buy_qty:
            flash("Sell quantity exceeds buy quantity. Trade is invalid.", "error")
            return redirect(url_for('trades.view_trade', trade_id=trade.id))

        # ✅ Proceed with entry
        entry = TradeEntry(
            quantity=quantity,
            price=price,
            date=date_obj,
            note=note,
            trade_id=trade.id
        )
        db.session.add(entry)

        # ✅ Set entry_date if not already set
        if not trade.entry_date:
            trade.entry_date = date_obj

        db.session.commit()
        flash("Buy entry added successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding buy entry: {str(e)}", "error")

    return redirect(url_for('trades.view_trade', trade_id=trade.id))



# add_exit – Log a Sell
@trades_bp.route('/trade/<int:trade_id>/exit', methods=['POST'])
@login_required
def add_exit(trade_id):
    trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    try:
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        date_str = request.form['date']
        date_obj = date.fromisoformat(date_str)
        note = request.form.get('note', '').strip()

        # ✅ Calculate total buy and sell quantities
        total_buy_qty = sum(e.quantity for e in trade.entries)
        total_sell_qty = sum(x.quantity for x in trade.exits)
        available_qty = total_buy_qty - total_sell_qty

        # ✅ Validate sell quantity
        if quantity > available_qty:
            flash(f"Cannot sell {quantity} units. Only {available_qty} available.", "error")
            return redirect(url_for('trades.view_trade', trade_id=trade.id))

        # ✅ Create exit
        exit = TradeExit(
            quantity=quantity,
            price=price,
            date=date_obj,
            note=note,
            trade_id=trade.id
        )
        db.session.add(exit)

        # ✅ Include new exit in total sell quantity
        updated_sell_qty = total_sell_qty + quantity

        if updated_sell_qty == total_buy_qty and total_buy_qty > 0:
            trade.status = "Closed"
            trade.exit_date = max([x.date for x in trade.exits] + [date_obj])  # Include new exit date

        db.session.commit()
        flash("Sell exit added successfully.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding sell exit: {str(e)}", "error")

    return redirect(url_for('trades.view_trade', trade_id=trade.id))


#edit_entry(entry_id) — Edit Buy Entry
@trades_bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = TradeEntry.query.get_or_404(entry_id)
    trade = entry.trade

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    if request.method == 'POST':
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            date_str = request.form['date']
            note = request.form.get('note', '').strip()
            date_obj = date.fromisoformat(date_str)

            entry.quantity = quantity
            entry.price = price
            entry.date = date_obj
            entry.note = note
            db.session.commit()
            flash("Buy entry updated successfully.", "success")
            return redirect(url_for('trades.view_trade', trade_id=trade.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating buy entry: {str(e)}", "error")

    return render_template('edit_entry.html', entry=entry, trade=trade)

#delete_entry(entry_id) — Delete Buy Entry
@trades_bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = TradeEntry.query.get_or_404(entry_id)
    trade = entry.trade

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash("Buy entry deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting buy entry: {str(e)}", "error")

    return redirect(url_for('trades.view_trade', trade_id=trade.id))

#edit_exit(exit_id) — Edit Sell Exit
@trades_bp.route('/exit/<int:exit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_exit(exit_id):
    exit = TradeExit.query.get_or_404(exit_id)
    trade = exit.trade

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    if request.method == 'POST':
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            date_str = request.form['date']
            note = request.form.get('note', '').strip()
            date_obj = date.fromisoformat(date_str)

            # Validate against available quantity
            total_buy_qty = sum(e.quantity for e in trade.entries)
            other_exits_qty = sum(x.quantity for x in trade.exits if x.id != exit.id)
            available_qty = total_buy_qty - other_exits_qty

            if quantity > available_qty:
                flash(f"Cannot sell {quantity} units. Only {available_qty} available.", "error")
                return redirect(url_for('trades.edit_exit', exit_id=exit.id))

            exit.quantity = quantity
            exit.price = price
            exit.date = date_obj
            exit.note = note
            db.session.commit()
            flash("Sell exit updated successfully.", "success")
            return redirect(url_for('trades.view_trade', trade_id=trade.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating sell exit: {str(e)}", "error")

    return render_template('edit_exit.html', exit=exit, trade=trade)

#delete_exit(exit_id) — Delete Sell Exit
@trades_bp.route('/exit/<int:exit_id>/delete', methods=['POST'])
@login_required
def delete_exit(exit_id):
    exit = TradeExit.query.get_or_404(exit_id)
    trade = exit.trade

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    try:
        db.session.delete(exit)
        db.session.commit()
        flash("Sell exit deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting sell exit: {str(e)}", "error")

    return redirect(url_for('trades.view_trade', trade_id=trade.id))

#edit_trade Route
@trades_bp.route('/trade/<int:trade_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    if request.method == 'POST':
        try:
            stock_name = request.form.get('stock_name', '').strip().upper()
            entry_date_str = request.form.get('entry_date')
            exit_date_str = request.form.get('exit_date')
            journal = request.form.get('journal', '').strip()

            trade.stock_name = stock_name
            trade.entry_date = date.fromisoformat(entry_date_str) if entry_date_str else None
            trade.exit_date = date.fromisoformat(exit_date_str) if exit_date_str else None
            trade.journal = journal

            db.session.commit()
            flash("Trade updated successfully.", "success")
            return redirect(url_for('trades.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating trade: {str(e)}", "error")

    return render_template('edit_trade.html', trade=trade)

#delete_trade Route
@trades_bp.route('/trade/<int:trade_id>/delete', methods=['POST'])
@login_required
def delete_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)

    if trade.user_id != current_user.id:
        flash("Unauthorized access.", "error")
        return redirect(url_for('trades.dashboard'))

    try:
        db.session.delete(trade)
        db.session.commit()
        flash("Trade deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting trade: {str(e)}", "error")

    return redirect(url_for('trades.dashboard'))

#trade_history() Route
@trades_bp.route('/history', methods=['GET'])
@login_required
def trade_history():
    stock_filter = request.args.get('stock', '').upper()
    date_range = request.args.get('date_range')
    sort_order = request.args.get('sort', 'desc')

    query = Trade.query.filter_by(user_id=current_user.id, status='Closed')

    if stock_filter:
        query = query.filter(Trade.stock_name == stock_filter)

    today = date.today()
    if date_range == 'last_month':
        start_date = today.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        query = query.filter(Trade.exit_date >= start_date)

    elif date_range == 'last_3_months':
        start_date = today - timedelta(days=90)
        query = query.filter(Trade.exit_date >= start_date)

    elif date_range == 'last_year':
        start_date = today - timedelta(days=365)
        query = query.filter(Trade.exit_date >= start_date)

    trades = query.order_by(Trade.exit_date.desc()).all()

    enriched = []
    for trade in trades:
        total_quantity = sum(e.quantity for e in trade.entries)
        total_invested = sum(e.quantity * e.price for e in trade.entries)
        avg_entry_price = round(total_invested / total_quantity, 2) if total_quantity else 0

        total_exited = sum(x.quantity * x.price for x in trade.exits)
        avg_exit_price = round(total_exited / total_quantity, 2) if total_quantity else 0

        realized_pnl = round(total_exited - total_invested, 2)
        total_days = (trade.exit_date - trade.entry_date).days if trade.entry_date and trade.exit_date else 0

        entry_notes = [e.note for e in trade.entries if e.note]
        exit_notes = [x.note for x in trade.exits if x.note]
        combined_notes = " | ".join(entry_notes + exit_notes)

        enriched.append({
            'stock_name': trade.stock_name.upper(),
            'entry_date': trade.entry_date,
            'exit_date': trade.exit_date,
            'avg_entry_price': avg_entry_price,
            'avg_exit_price': avg_exit_price,
            'total_quantity': total_quantity,
            'realized_pnl': realized_pnl,
            'total_days': total_days,
            'notes': combined_notes
        })

    enriched.sort(key=lambda t: t['realized_pnl'], reverse=(sort_order == 'desc'))
    stock_list = sorted(set(t.stock_name for t in trades))

    return render_template('trade_history.html',
                           trades=enriched,
                           stock_list=stock_list,
                           selected_stock=stock_filter,
                           selected_range=date_range,
                           sort=sort_order)


#export logic
@trades_bp.route('/history/export')
@login_required
def export_history():
    stock_filter = request.args.get('stock', '').upper()
    date_range = request.args.get('date_range')
    sort_order = request.args.get('sort', 'desc')

    query = Trade.query.filter_by(user_id=current_user.id, status='Closed')

    if stock_filter:
        query = query.filter(Trade.stock_name == stock_filter)

    today = date.today()
    if date_range == 'last_month':
        start_date = today.replace(day=1) - timedelta(days=1)
        start_date = start_date.replace(day=1)
        query = query.filter(Trade.exit_date >= start_date)
    elif date_range == 'last_3_months':
        start_date = today - timedelta(days=90)
        query = query.filter(Trade.exit_date >= start_date)
    elif date_range == 'last_year':
        start_date = today - timedelta(days=365)
        query = query.filter(Trade.exit_date >= start_date)

    trades = query.order_by(Trade.exit_date.desc()).all()

    data = []
    for trade in trades:
        total_quantity = sum(e.quantity for e in trade.entries)
        total_invested = sum(e.quantity * e.price for e in trade.entries)
        avg_entry_price = round(total_invested / total_quantity, 2) if total_quantity else 0

        total_exited = sum(x.quantity * x.price for x in trade.exits)
        avg_exit_price = round(total_exited / total_quantity, 2) if total_quantity else 0

        realized_pnl = round(total_exited - total_invested, 2)
        total_days = (trade.exit_date - trade.entry_date).days if trade.entry_date and trade.exit_date else 0

        entry_notes = [e.note for e in trade.entries if e.note]
        exit_notes = [x.note for x in trade.exits if x.note]
        combined_notes = " | ".join(entry_notes + exit_notes)

        data.append({
            'Stock Name': trade.stock_name.upper(),
            'Entry': trade.entry_date.strftime('%d-%b-%Y') if trade.entry_date else '',
            'Exit': trade.exit_date.strftime('%d-%b-%Y') if trade.exit_date else '',
            'Entry (Avg)': avg_entry_price,
            'Exit (Avg)': avg_exit_price,
            'Quantity': total_quantity,
            'Duration': f"{total_days} days",
            'Realized P&L': realized_pnl,
            'Notes': combined_notes
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Completed Trades')

    output.seek(0)
    return send_file(output,
                     download_name='completed_trades.xlsx',
                     as_attachment=True,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
