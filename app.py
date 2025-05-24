from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Dummy structure
users = {}
expenses_data = {}  # { user_id: { category_name: [{date, amount}, ...] } }
expense_counter = 1

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and users[username]['password'] == password:
            session['user_id'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    global expense_counter
    user_id = session.get('user_id')
    categories = list(expenses_data[user_id].keys()) if user_id and user_id in expenses_data else []
    if request.method == 'POST':
        category = request.form.get('category_select') or request.form.get('category')
        date = request.form['date']
        amount = float(request.form['amount'])
        note = request.form.get('note', '')

        if user_id:
            if category not in expenses_data[user_id]:
                expenses_data[user_id][category] = []
            expenses_data[user_id][category].append({'id': expense_counter, 'date': date, 'amount': amount, 'note': note})
            expense_counter += 1

        return redirect(url_for('dashboard'))

    return render_template('add_expense.html', categories=categories)

@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category = request.form['category']
        user_id = session.get('user_id')
        if user_id and category not in expenses_data[user_id]:
            expenses_data[user_id][category] = []
        return redirect(url_for('dashboard'))

    return render_template('add_category.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Date filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    categories = []
    total_all = 0
    
    if user_id in expenses_data:
        for category_name, expenses in expenses_data[user_id].items():
            # Sort and filter expenses by date
            filtered_expenses = expenses
            if start_date:
                filtered_expenses = [e for e in filtered_expenses if e['date'] >= start_date]
            if end_date:
                filtered_expenses = [e for e in filtered_expenses if e['date'] <= end_date]
            sorted_expenses = sorted(filtered_expenses, key=lambda x: x['date'])
            category_total = sum(expense['amount'] for expense in sorted_expenses)
            total_all += category_total
            categories.append({
                'name': category_name,
                'expenses': sorted_expenses,
                'total': category_total
            })
    
    return render_template('dashboard.html', categories=categories, total_all=total_all, username=user_id, start_date=start_date or '', end_date=end_date or '')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users:
            flash('Username already exists')
        else:
            users[username] = {'password': password}
            expenses_data[username] = {}
            session['user_id'] = username
            return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    for category, expenses in expenses_data.get(user_id, {}).items():
        for idx, expense in enumerate(expenses):
            if expense.get('id') == expense_id:
                if request.method == 'POST':
                    expense['date'] = request.form['date']
                    expense['amount'] = float(request.form['amount'])
                    expense['note'] = request.form.get('note', '')
                    return redirect(url_for('dashboard'))
                return render_template('edit_expense.html', expense=expense, category=category)
    flash('Expense not found')
    return redirect(url_for('dashboard'))

@app.route('/delete_expense/<int:expense_id>')
def delete_expense(expense_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    for category, expenses in expenses_data.get(user_id, {}).items():
        for idx, expense in enumerate(expenses):
            if expense.get('id') == expense_id:
                del expenses[idx]
                break
    return redirect(url_for('dashboard'))

@app.route('/delete_category/<category_name>')
def delete_category(category_name):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    if category_name in expenses_data.get(user_id, {}):
        del expenses_data[user_id][category_name]
    return redirect(url_for('dashboard'))

@app.route('/edit_category/<category_name>', methods=['GET', 'POST'])
def edit_category(category_name):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_name = request.form['new_name']
        if new_name and new_name != category_name:
            # Move expenses to new category name
            expenses = expenses_data[user_id].pop(category_name, [])
            expenses_data[user_id][new_name] = expenses
        return redirect(url_for('dashboard'))
    return render_template('edit_category.html', category_name=category_name)

@app.route('/download_csv')
def download_csv():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Category', 'Date', 'Amount', 'Note'])
    if user_id in expenses_data:
        for category_name, expenses in expenses_data[user_id].items():
            filtered_expenses = expenses
            if start_date:
                filtered_expenses = [e for e in filtered_expenses if e['date'] >= start_date]
            if end_date:
                filtered_expenses = [e for e in filtered_expenses if e['date'] <= end_date]
            for expense in filtered_expenses:
                writer.writerow([category_name, expense['date'], expense['amount'], expense.get('note', '')])
    output.seek(0)
    return app.response_class(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=expenses.csv'}
    )
