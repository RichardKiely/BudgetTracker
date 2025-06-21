from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    selected_category = request.args.get('category')
    conn = sqlite3.connect('budget.db')
    c = conn.cursor()

    if selected_category and selected_category != 'all':
        c.execute('SELECT * FROM transactions WHERE category = ? ORDER BY date DESC', (selected_category,))
    else:
        c.execute('SELECT * FROM transactions ORDER BY date DESC')

    transactions = c.fetchall()

    income = sum(t[3] for t in transactions if t[4] == 'income')
    expenses = sum(t[3] for t in transactions if t[4] == 'expense')
    balance = income - expenses

    c.execute('SELECT DISTINCT category FROM transactions')
    categories = [row[0] for row in c.fetchall()]

    conn.close()

    return render_template(
        'index.html',
        transactions=transactions,
        income=income,
        expenses=expenses,
        balance=balance,
        categories=categories,
        selected_category=selected_category or 'all'
    )

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date = request.form['date']
        description = request.form['description']
        amount = float(request.form['amount'])
        type = request.form['type']
        category = request.form['category']

        conn = sqlite3.connect('budget.db')
        c = conn.cursor()
        c.execute('INSERT INTO transactions (date, description, amount, type, category) VALUES (?, ?, ?, ?, ?)',
                  (date, description, amount, type, category))
        conn.commit()
        conn.close()

        return redirect('/')
    return render_template('add.html')

if __name__ == '__main__':
    if not os.path.exists('budget.db'):
        init_db()
    app.run(debug=True)
