from flask import Blueprint, render_template, request, flash
from flask_wtf.csrf import validate_csrf, CSRFError  # ✅ Add CSRF imports

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/risk', methods=['GET', 'POST'])
def risk_calculator():
    result = None
    if request.method == 'POST':
        try:
            validate_csrf(request.form.get('csrf_token'))  # ✅ Validate CSRF

            investment = float(request.form['investment'])
            current_price = float(request.form['current_price'])
            sl_price = float(request.form['sl_price'])

            risk_per_share = current_price - sl_price
            risk_pct_of_price = round((risk_per_share / current_price) * 100, 2) if current_price > 0 else 0

            def calc_qty(risk_pct):
                max_affordable_qty = int(investment / current_price)
                risk_amount = investment * risk_pct
                risk_per_share = current_price - sl_price

                max_risk_qty = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
                quantity = min(max_affordable_qty, max_risk_qty)

                return {
                    'risk_pct': risk_pct * 100,
                    'risk_amount': round(risk_amount, 2),
                    'quantity': quantity,
                    'max_affordable_qty': max_affordable_qty
                }

            result = {
                'investment': investment,
                'current_price': current_price,
                'sl_price': sl_price,
                'risk_per_share': risk_per_share,
                'risk_pct_of_price': risk_pct_of_price,
                'levels': [
                    calc_qty(0.05),
                    calc_qty(0.04),
                    calc_qty(0.03),
                    calc_qty(0.02),
                    calc_qty(0.01)
                ]
            }

        except CSRFError:
            flash("Invalid or missing CSRF token.", "danger")
        except ValueError:
            result = {'error': 'Invalid input. Please enter numeric values.'}

    return render_template('risk_calculator.html', result=result)
