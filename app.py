import matplotlib
matplotlib.use('Agg')

import base64
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, Response
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/calculate_yield', methods=['POST'])
def calculate_yield():
    # Retrieve input values from the form
    purchase_price = float(request.form['purchasePrice'])
    deposit_percentage = float(request.form['depositPercentage'])
    mortgage_rate = float(request.form['mortgageRate'])
    mortgage_period = float(request.form['mortgagePeriod'])
    tax_percentage = float(request.form['taxPercentage'])
    maintenance_fee_percentage = float(request.form['maintenanceFeePercentage'])
    monthly_rent = float(request.form.get('monthlyRent'))
    refurbishment_cost = float(request.form.get('refurbishmentCost'))
    legal_fees = float(request.form.get('legalFees'))
    other_annual_expenses = float(request.form.get('otherAnnualExpenses'))

    # Calculate the stamp duty based on the purchase price
    if purchase_price <= 500000:
        stamp_duty = purchase_price * 0.03
    elif purchase_price <= 1000000:
        stamp_duty = 15000 + (purchase_price - 500000) * 0.05
    else:
        stamp_duty = 50000 + (purchase_price - 1000000) * 0.1

    # Perform calculations
    deposit_amount = (deposit_percentage / 100) * purchase_price
    total_initial_investment = deposit_amount + stamp_duty + refurbishment_cost + legal_fees
    mortgage_amount = purchase_price - deposit_amount
    annual_mortgage = (mortgage_amount * (mortgage_rate / 100))
    monthly_mortgage = (annual_mortgage / 12)
    annual_rent = (monthly_rent * 12)
    annual_maintenance = (annual_rent * (maintenance_fee_percentage / 100))
    annual_expenses_without_mortgage_payments = (annual_maintenance + other_annual_expenses)
    total_annual_expenses = (annual_expenses_without_mortgage_payments + annual_mortgage)
    gross_annual_profit = (annual_rent - annual_expenses_without_mortgage_payments)
    gross_yield = ((gross_annual_profit / total_initial_investment) * 100)
    net_annual_profit_before_tax = (gross_annual_profit - annual_mortgage)
    net_annual_profit_after_tax = (net_annual_profit_before_tax - (net_annual_profit_before_tax * (tax_percentage / 100)))
    net_yield_before_tax = ((net_annual_profit_before_tax / total_initial_investment) * 100)
    net_yield_after_tax = ((net_annual_profit_after_tax / total_initial_investment) * 100)

    # Generate the graph
    x = ['Gross Yield', 'Net Yield']
    y = [gross_yield, net_yield_before_tax]

    fig, ax = plt.subplots()
    ax.bar(x, y)
    ax.set_ylabel('Yield (%)')
    ax.set_title('Rental Property Yield')

    # Save the graph to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convert the graph image to base64 string
    graph_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Prepare the response data as a JSON object
    response_data = {
        'depositAmount': deposit_amount,
        'mortgageAmount': mortgage_amount,
        'stampDuty': stamp_duty,
        'refurbishmentCost': refurbishment_cost,
        'legalFees': legal_fees,
        'totalInitialInvestment': total_initial_investment,
        'annualRent': annual_rent,
        'grossAnnualProfit': gross_annual_profit,
        'netAnnualProfitBeforeTax': net_annual_profit_before_tax,
        'netAnnualProfitAfterTax': net_annual_profit_after_tax,
        'monthlyRent': monthly_rent,
        'annualMaintenance': annual_maintenance,
        'annualMortgage': annual_mortgage,
        'monthlyMortgage': monthly_mortgage,
        'annualExpensesWithoutMortgagePayments': annual_expenses_without_mortgage_payments,
        'totalAnnualExpenses': total_annual_expenses,
        'grossYield': gross_yield,
        'netYieldBeforeTax': net_yield_before_tax,
        'netYieldAfterTax': net_yield_after_tax,
        'graphData': graph_data
    }

    # Return the response data as JSON
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
