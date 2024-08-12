from flask import Flask, render_template, request, jsonify
from decimal import Decimal
from crypto_price import get_crypto_price
from gemini_integration.geminiAPI import env
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Set up the SQLAlchemy part
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///investment_history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Investment model
class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coin_name = db.Column(db.String(50), nullable=False)
    buy_price = db.Column(db.Numeric, nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    current_price = db.Column(db.Numeric, nullable=False)
    profit_loss = db.Column(db.String(50), nullable=False)
    advice = db.Column(db.Text, nullable=True)

# Flag to check if tables are created
tables_created = False

@app.before_request
def create_tables():
    global tables_created
    if not tables_created:
        db.create_all()
        tables_created = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/main')
def main():
    return render_template('main.html')

def get_investment_advice(user_data):
    API_KEY = env('API_KEY')
    if not API_KEY:
        return "API key not found. Please set the API_KEY environment variable."
    
    genai.configure(api_key=API_KEY)
    
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    
    chat_session = model.start_chat(history=[])

    user_message = (
        f"You're a financial advisor and will give me advice based on the information I provide. "
        f"I invested in {user_data['coin_name']}, bought at ${user_data['buy_price']} per coin, "
        f"and now the price is ${user_data['current_price']}. I have {user_data['amount']} coins. "
        f"My profit/loss is {user_data['profit_loss']['amount']} which is a {user_data['profit_loss']['type']}."
    )
    
    response = chat_session.send_message(user_message)
    
    raw_advice = response.text if response and response.text else "No advice returned"
    print("Raw advice:", raw_advice)  # Log the raw response for debugging
    
    if response and response.text:
        advice = clean_advice_text(response.text)
    else:
        advice = "Could not generate investment advice at this time."

    return advice

import re

def clean_advice_text(advice):
    # Remove stars and extra line breaks
    advice = advice.replace('*', '')
    ##advice = advice.replace('\n\n\n', '\n')  # Handle multiple newlines

    # Replace numbered lists with bullet points
    advice = re.sub(r'^\d+\.\s+', '• ', advice, flags=re.MULTILINE)
    
    # Optionally, replace multiple spaces with a single space
    advice = ' '.join(advice.split())
    
    return advice.strip()



def clean_advice_text(advice):
    # Remove stars and multiple newlines
    advice = advice.replace('*', '')
    advice = advice.replace('\n\n', '\n')  # Remove extra line breaks
    advice = advice.replace('\n\n\n', '\n')  # Handle multiple newlines

    # Additional cleanup if needed
    advice = advice.strip()
    
    # Optionally replace multiple spaces with a single space
    advice = ' '.join(advice.split())
    
    return advice

def calculate_profit_loss(buy_price, current_price, amount):
    profit_loss = (current_price - buy_price) * amount
    if profit_loss > 0:
        return {'type': 'profit', 'amount': profit_loss}
    else:
        return {'type': 'loss', 'amount': abs(profit_loss)}

@app.route('/advice', methods=['POST'])
def advice():
    data = request.get_json()
    coin_name = data['coin_name']
    buy_price = Decimal(data['buy_price'])
    amount = Decimal(data['amount'])

    current_price = get_crypto_price(coin_name)
    if current_price is None:
        return jsonify({'error': "Unable to fetch the current price for the specified coin."}), 400
    
    profit_loss = calculate_profit_loss(buy_price, Decimal(current_price), amount)

    user_data = {
        'coin_name': coin_name,
        'buy_price': buy_price,
        'amount': amount,
        'current_price': current_price,
        'profit_loss': profit_loss
    }

    advice = get_investment_advice(user_data)

    return jsonify({'user_data': user_data, 'advice': advice})

@app.route('/investments', methods=['POST'])
def add_investment():
    data = request.get_json()
    coin_name = data['coin_name']
    buy_price = Decimal(data['buy_price'])
    amount = Decimal(data['amount'])

    current_price = get_crypto_price(coin_name)
    if current_price is None:
        return jsonify({'error': "Unable to fetch the current price for the specified coin."}), 400
    
    profit_loss = calculate_profit_loss(buy_price, Decimal(current_price), amount)

    investment = Investment(
        coin_name=coin_name,
        buy_price=buy_price,
        amount=amount,
        current_price=Decimal(current_price),
        profit_loss=f"{profit_loss['type']} of {profit_loss['amount']}",
    )
    db.session.add(investment)
    db.session.commit()

    return jsonify({'message': 'Investment added successfully'})

@app.route('/investments', methods=['GET'])
def get_investments():
    investments = Investment.query.all()
    investment_list = []

    for inv in investments:
        current_price = get_crypto_price(inv.coin_name)
        if current_price is None:
            return jsonify({'error': "Unable to fetch the current price for the specified coin."}), 400

        investment_list.append({
            'id': inv.id,
            'coin_name': inv.coin_name,
            'buy_price': str(inv.buy_price),
            'amount': str(inv.amount),
            'current_price': current_price,
            'profit_loss': inv.profit_loss,
        })

    return jsonify(investment_list)

@app.route('/investments/<int:id>', methods=['PUT'])
def update_investment(id):
    investment = Investment.query.get_or_404(id)
    data = request.get_json()
    coin_name = data['coin_name']
    buy_price = Decimal(data['buy_price'])
    amount = Decimal(data['amount'])

    current_price = get_crypto_price(coin_name)
    if current_price is None:
        return jsonify({'error': "Unable to fetch the current price for the specified coin."}), 400
    
    profit_loss = calculate_profit_loss(buy_price, Decimal(current_price), amount)

    investment.coin_name = coin_name
    investment.buy_price = buy_price
    investment.amount = amount
    investment.current_price = Decimal(current_price)
    investment.profit_loss = f"{profit_loss['type']} of {profit_loss['amount']}"

    db.session.commit()

    return jsonify({'message': 'Investment updated successfully'})

@app.route('/investments/<int:id>', methods=['DELETE'])
def delete_investment(id):
    investment = Investment.query.get_or_404(id)
    db.session.delete(investment)
    db.session.commit()
    return jsonify({'message': 'Investment deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
