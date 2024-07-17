//app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'bank'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_customer', methods=['GET', 'POST'])
def new_customer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']
        dob = request.form['dob']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Customers (name, address, phone, email, dob) VALUES (%s, %s, %s, %s, %s)', (name, address, phone, email, dob))
        mysql.connection.commit()
        cursor.close()
        flash('Customer registered successfully!')
        return redirect(url_for('new_customer'))

    return render_template('new_customer.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        customerId = request.form['customerId']
        branchId = request.form['branchId']
        accountType = request.form['accountType']
        balance = request.form['balance']
        dateOpened = datetime.now().strftime('%Y-%m-%d')

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO Accounts (bid, acc_type, balance, date_opened, cus_id) VALUES (%s, %s, %s, %s, %s)', (branchId, accountType, balance, dateOpened, customerId))
        mysql.connection.commit()
        cursor.close()
        flash('Account created successfully!')
        return redirect(url_for('create_account'))

    return render_template('create_account.html')

@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if request.method == 'POST':
        accountNumber = request.form['accountNumber']
        transactionType = request.form['transactionType']
        amount = float(request.form['amount'])

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT balance FROM Accounts WHERE id = %s', [accountNumber])
        account = cursor.fetchone()

        if account:
            new_balance = account['balance'] + amount if transactionType == 'credit' else account['balance'] - amount
            if new_balance < 0:
                flash('Insufficient funds for debit transaction!')
            else:
                cursor.execute('UPDATE Accounts SET balance = %s WHERE id = %s', (new_balance, accountNumber))
                transaction_date = datetime.now().strftime('%Y-%m-%d')
                transaction_time = datetime.now().strftime('%H:%M:%S')
                cursor.execute('INSERT INTO transaction_details (transaction_date, transaction_time, amount, acc_num) VALUES (%s, %s, %s, %s)', (transaction_date, transaction_time, amount, accountNumber))
                mysql.connection.commit()
                flash('Transaction successful! New balance: ₹' + str(new_balance))
        else:
            flash('Account not found!')

        cursor.close()
        return redirect(url_for('transaction'))

    return render_template('credit_debit.html')

@app.route('/calculate_emi', methods=['GET', 'POST'])
def calculate_emi():
    if request.method == 'POST':
        accountNumber = request.form['accountNumber']
        loanAmount = float(request.form['loanAmount'])
        interestRate = float(request.form['interestRate'])
        loanPeriod = int(request.form['loanPeriod'])

        monthly_rate = interestRate / (12 * 100)
        emi = (loanAmount * monthly_rate) / (1 - (1 + monthly_rate) ** (-loanPeriod * 12))
        emi = round(emi, 2)

        cursor = mysql.connection.cursor()
        issue_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('INSERT INTO Loan (acc_num, loan_amt, issue_date, loan_status) VALUES (%s, %s, %s, %s)', (accountNumber, loanAmount, issue_date, 'active'))
        mysql.connection.commit()
        cursor.close()
        flash(f'EMI: ₹{emi} per month for {loanPeriod} years.')
        return redirect(url_for('calculate_emi'))

    return render_template('loans.html')

if __name__ == '__main__':
    app.run(debug=True)
