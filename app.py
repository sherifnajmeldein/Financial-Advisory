from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
from api import get_crypto_price
from env_loader import env
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

def get_investment_advice(user_data):
    API_KEY = env('API_KEY')  # Access the key from the environment
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
    
    if response and response.text:
        advice = response.text.strip()
    else:
        advice = "Could not generate investment advice at this time."

    return advice

def calculate_profit_loss(buy_price, current_price, amount):
    profit_loss = (current_price - buy_price) * amount
    if profit_loss > 0:
        return {'type': 'profit', 'amount': profit_loss}
    else:
        return {'type': 'loss', 'amount': abs(profit_loss)}

@app.route('/result', methods=['POST'])
def result():
    coin_name = request.form['coin_name']
    buy_price = float(request.form['buy_price'])
    amount = float(request.form['amount'])

    current_price = get_crypto_price(coin_name)
    if current_price is None:
        return render_template('error.html', message="Unable to fetch the current price for the specified coin.")
    
    profit_loss = calculate_profit_loss(buy_price, current_price, amount)

    user_data = {
        'coin_name': coin_name,
        'buy_price': buy_price,
        'amount': amount,
        'current_price': current_price,
        'profit_loss': profit_loss
    }

    advice = get_investment_advice(user_data)
    return render_template('result.html', user_data=user_data, advice=advice)

if __name__ == '__main__':
    app.run(debug=True)
