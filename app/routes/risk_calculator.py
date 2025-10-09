from flask import Blueprint, render_template, request

risk_bp = Blueprint('risk', __name__)
@risk_bp.route('/risk', methods=['GET', 'POST'])
def risk_calculator():
    result = None
    if request.method == 'POST':
        try:
            investment = float(request.form['investment'])
            current_price = float(request.form['current_price'])
            sl_price = float(request.form['sl_price'])

            risk_per_share = current_price - sl_price

            def calc_qty(risk_pct):
                risk_amount = investment * risk_pct
                quantity = int(risk_amount / risk_per_share) if risk_per_share > 0 else 0
                return {'risk_pct': risk_pct * 100, 'risk_amount': risk_amount, 'quantity': quantity}

            result = {
                'investment': investment,
                'current_price': current_price,
                'sl_price': sl_price,
                'risk_per_share': risk_per_share,
                'levels': [
                    calc_qty(0.05),
                    calc_qty(0.04),
                    calc_qty(0.03),
                    calc_qty(0.02),
                    calc_qty(0.01)
                ]
            }
        except ValueError:
            result = {'error': 'Invalid input. Please enter numeric values.'}

    return render_template('risk_calculator.html', result=result)
