import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import yaml
from werkzeug.security import generate_password_hash, check_password_hash

import time
import datetime

app = Flask(__name__)

app.secret_key = '1011'

db = yaml.load(open('bank.yaml'),Loader=yaml.Loader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

ts = time.time()
timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

mysql = MySQL(app)
@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers")
    data1 = cursor.fetchall()
    return render_template('bank.html', data=data1)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        msg = ''
        f = 0
        balance = session['balance']
        email = session['email']
        details = request.form
        receiver = details['rname']
        amount = details['amount']
        name = session['sname']
        id = session['id']
        cur = mysql.connection.cursor()
        if amount == '':
            amt = int('0'+amount)
        else:
            amt = int(amount)

        res = cur.execute("SELECT name FROM customers")
        record = cur.fetchall()
        c = 0
        for row in record:
            rec = ''.join(row)
            if receiver == '' or receiver != ''.join(row):
                c = c+1
        
        if(c==res):
            msg = "Receiver Not Present or Field Can't be empty"
            return render_template('make.html', msg=msg,name=name,id=id,email=email,balance=balance)
        else:
            c = 0
            print(name)
            cur.execute("SELECT curr_bal FROM customers where name=name")
            record = cur.fetchone()
            amount = int(record[0])
            if amt == 0 or amt>amount:
                f = 1
                msg = "Amount not Sufficient or Field Can't be empty"
                return render_template('make.html', msg=msg,name=name,id=id,email=email,balance=balance)

        if f==0:
            cur.execute("INSERT INTO transactions(sname, rname, amount) VALUES (%s, %s, %s)",(session['sname'],receiver, amt))
            mysql.connection.commit()
            name = session['sname']
            sen = amount-amt
            cur.execute("UPDATE CUSTOMERS SET curr_bal=%s WHERE name=%s",(sen,name))
            cur.execute("SELECT curr_bal FROM customers where name=%s",(receiver))
            record = cur.fetchone()
            amount = int(record[0])
            rec = amount+amt
            cur.execute("UPDATE CUSTOMERS SET curr_bal=%s WHERE name=%s",(rec, receiver))
            mysql.connection.commit()
            cur.close()
            return redirect('/')

# @app.route("/transactions", methods=['GET', 'POST'])
# def transactions():
#     if request.method == 'POST' and 'reciever' in request.form and 'amount' in request.form and 'pname' in request.form and 'pbal' in request.form:
#         reciever = request.form['reciever']
#         amount = float(request.form['amount'])
#         amount1 = float(request.form['amount'])
#         sender = request.form['pname']
#         scurrbal = float(request.form['pbal'])
#         cursor = mysql.connection.cursor()
#         sbal = scurrbal - amount
#         cursor.execute("SELECT curr_bal FROM customers WHERE name=%s", (reciever,))
#         rcurr_bal = cursor.fetchone()
#         rcurrbal = float(rcurr_bal[0])
#         rbal = rcurrbal + amount1
#         print(rcurrbal)
#         print(rbal)
#         cursor.execute("SELECT * FROM transactions WHERE sname=%s", (sender,))

#         tid = cursor.fetchall()
#         if scurrbal >= amount:
#             cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (rbal, reciever,))
#             cursor.execute("UPDATE customers SET curr_bal=%s where name=%s", (sbal, sender,))
#             cursor.execute("INSERT INTO transactions(sname,rname,amount) VALUES ( %s, %s,%s)",
#                            (sender, reciever, amount,))
#             mysql.connection.commit()
#         else:
#             return "Insufficient Funds!"
#         return redirect('/')


@app.route('/history')
def transhis():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY time DESC')
    data1 = cursor.fetchall()
    return render_template('transhis.html', data=data1)

@app.route('/transact', methods=['POST','GET'])
def transact():
    id = request.form['cid']
    name = request.form['cname']
    balance = int(float(request.form['cbal']))
    email = request.form['cemail']
    session['sname'] = name
    session['id'] = id
    session['balance'] = balance
    session['email'] = email
    return render_template('make.html', id=id,name=name,balance=balance,email=email)


if __name__ == "__main__":
    app.run(debug=True)