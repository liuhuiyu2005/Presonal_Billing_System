from flask import Flask, request, jsonify, render_template
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  amount REAL NOT NULL,
                  category TEXT NOT NULL,
                  description TEXT,
                  date TEXT NOT NULL,
                  type TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = c.fetchall()
    conn.close()
    
    result = []
    for trans in transactions:
        result.append({
            'id': trans[0],
            'amount': trans[1],
            'category': trans[2],
            'description': trans[3],
            'date': trans[4],
            'type': trans[5]
        })
    return jsonify(result)

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions (amount, category, description, date, type) VALUES (?, ?, ?, ?, ?)',
              (data['amount'], data['category'], data['description'], data['date'], data['type']))
    conn.commit()
    conn.close()
    return jsonify({'message': '交易添加成功'})

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': '交易删除成功'})

@app.route('/api/summary')
def get_summary():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    
    # 总收入
    c.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
    total_income = c.fetchone()[0] or 0
    
    # 总支出
    c.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
    total_expense = c.fetchone()[0] or 0
    
    # 按类别统计
    c.execute('SELECT category, type, SUM(amount) FROM transactions GROUP BY category, type')
    category_data = c.fetchall()
    
    conn.close()
    
    return jsonify({
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'category_data': [{'category': item[0], 'type': item[1], 'amount': item[2]} for item in category_data]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)