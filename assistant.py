import sqlite3
import os
from datetime import datetime

# You'll need to install openai: pip install openai
from openai import OpenAI

DB_NAME = "finance.db"

def setup_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY, date TEXT, amount REAL, category TEXT, description TEXT)''')
    conn.commit()
    conn.close()

def add_expense(amount, category, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
              (date, amount, category, description))
    conn.commit()
    conn.close()
    print(f"Added: ${amount} for {description} ({category})")

def get_recent_expenses():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, amount, category, description FROM expenses ORDER BY date DESC LIMIT 50")
    expenses = c.fetchall()
    conn.close()
    return expenses

def view_expenses_and_stats():
    expenses = get_recent_expenses()
    if not expenses:
        print("\nNo expenses found. Add some first!")
        return

    print("\n--- Your Expenses ---")
    total = 0
    for expense in expenses:
        date, amount, category, desc = expense
        print(f"[{date}] {category}: ${amount:.2f} - {desc}")
        total += amount

    count = len(expenses)
    average = total / count if count > 0 else 0
    
    print("-" * 25)
    print(f"Total Spent:   ${total:.2f}")
    print(f"Average Spent: ${average:.2f}")

def search_by_category(search_term):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT date, amount, category, description FROM expenses WHERE category LIKE ? ORDER BY date DESC", (f'%{search_term}%',))
    expenses = c.fetchall()
    conn.close()
    
    if not expenses:
        print(f"\nNo expenses found in category matching '{search_term}'.")
        return

    print(f"\n--- Expenses for '{search_term}' ---")
    total = 0
    for expense in expenses:
        date, amount, category, desc = expense
        print(f"[{date}] {category}: ${amount:.2f} - {desc}")
        total += amount
    
    print("-" * 25)
    print(f"Total Spent in '{search_term}': ${total:.2f}")

def get_ai_advice():
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        print("\n[Notice] No OpenAI API Key found.")
        user_key = input("Please enter your API Key now (or press Enter for a mock response): ").strip()
        if user_key:
            os.environ["OPENAI_API_KEY"] = user_key
            api_key = user_key

    expenses = get_recent_expenses()
    
    if not expenses:
        return "No expenses to analyze yet. Add some first!"
        
    if not api_key:
        return (
            "🤖 [MOCK AI RESPONSE - No API Key Provided]\n"
            "I see you have some recent expenses! To balance this out, I recommend cutting back on 'Entertainment' for the next two weeks. "
            "Also, consider starting an emergency fund for unexpected costs. Great job tracking your expenses!"
        )

    prompt = f"Act as a financial advisor. Here are my recent expenses:\n{expenses}\nGive me a short, friendly summary of my spending and 1-2 tips to save money."
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

if __name__ == "__main__":
    setup_db()
    
    while True:
        print("\n--- AI Finance Assistant ---")
        print("1. Add Expense")
        print("2. View Expenses & Stats")
        print("3. Search by Category")
        print("4. Get AI Financial Advice")
        print("5. Quit")
        choice = input("Choose an option (1-5): ")
        
        if choice == '1':
            try:
                amount = float(input("Amount: $"))
                category = input("Category (e.g., Food, Rent, Fun): ")
                desc = input("Description: ")
                add_expense(amount, category, desc)
            except ValueError:
                print("Invalid amount. Please enter a number.")
        elif choice == '2':
            view_expenses_and_stats()
        elif choice == '3':
            search_term = input("Enter category to search for (e.g., Food, Travel): ")
            search_by_category(search_term)
        elif choice == '4':
            print("\nThinking... \n")
            print(get_ai_advice())
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")
