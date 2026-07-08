from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
import os
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
DB_NAME = "finance.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect('/jarvis')

@app.route('/jarvis')
def index():
    return render_template('index.html')

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category', '')
    conn = get_db_connection()
    if category:
        expenses = conn.execute("SELECT * FROM expenses WHERE category LIKE ? ORDER BY date DESC", (f'%{category}%',)).fetchall()
    else:
        expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC LIMIT 50").fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in expenses])

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description')
    date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db_connection()
    conn.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
                 (date, amount, category, description))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/advice', methods=['GET'])
def get_advice():
    api_key = os.environ.get("OPENAI_API_KEY")
    conn = get_db_connection()
    expenses = conn.execute("SELECT date, amount, category, description FROM expenses ORDER BY date DESC LIMIT 50").fetchall()
    conn.close()
    
    if not expenses:
        return jsonify({"advice": "No expenses to analyze yet. Add some first!"})
        
    if not api_key:
        return jsonify({"advice": "🤖 **MOCK AI RESPONSE**\n\nI see you have some recent expenses! To balance this out, I recommend cutting back on 'Entertainment' for the next two weeks. Also, consider starting an emergency fund for unexpected costs. Great job tracking your expenses!\n\n*(Note: Set your OPENAI_API_KEY environment variable to get real advice!)*"})

    expenses_text = "\n".join([f"{e['date']} - {e['category']}: ${e['amount']} ({e['description']})" for e in expenses])
    prompt = f"Act as a financial advisor. Here are my recent expenses:\n{expenses_text}\nGive me a short, friendly summary of my spending and 1-2 tips to save money. Format with simple markdown if helpful."
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return jsonify({"advice": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"advice": f"AI Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
