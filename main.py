from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from forms import ReceiveForm
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = '245GA'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '7227'
app.config['MYSQL_DB'] = 'bloodbank'

# Intialize MySQL
mysql = MySQL(app)

# http://localhost:5000/ - this will be the homepage 
@app.route('/', methods=['GET'])
def landingpage():
    return render_template('landingPage.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == "POST":
        details = request.form
        name = details['name']
        email = details['email']
        phone = details['phone']
        message = details['message']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact VALUES (NULL, %s, %s, %s, %s)", (name, email, phone, message))
        mysql.connection.commit()
        cur.close()
        return('Message sent success')
    return render_template('contact.html')

# http://localhost:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['uid'] = account['uid']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('uid', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
# @app.route('/pythonlogin/register', methods=['GET', 'POST'])
# def register():
    # # Output message if something goes wrong...
    # msg = ''
    # # Check if "username", "password" and "email" POST requests exist (user submitted form)
    # if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
    #     # Create variables for easy access
    #     username = request.form['username']
    #     password = request.form['password']
    #     email = request.form['email']
    #     # Check if account exists using MySQL
    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
    #     account = cursor.fetchone()
    #     # If account exists show error and validation checks
    #     if account:
    #         msg = 'Account already exists!'
    #     elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
    #         msg = 'Invalid email address!'
    #     elif not re.match(r'[A-Za-z0-9]+', username):
    #         msg = 'Username must contain only characters and numbers!'
    #     elif not username or not password or not email:
    #         msg = 'Please fill out the form!'
    #     else:
    #         # Account doesnt exists and the form data is valid, now insert new account into accounts table
    #         cursor.execute('INSERT INTO accounts(username, password, email) VALUES (NULL, %s, %s, %s)', (username, password, email))
    #         mysql.connection.commit()
    #         msg = 'You have successfully registered!'
    # elif request.method == 'POST':
    #     # Form is empty... (no POST data)
    #     msg = 'Please fill out the form!'
    # # Show registration form with message (if any)

# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        details = request.form
        username = details['username']
        password = details['password']
        email = details['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO accounts VALUES (NULL, %s, %s, %s)", (username, password, email))
        mysql.connection.commit()
        msg = 'You have successfully registered!'
        cur.close()
        return('You have successfully registered')
    # return render_template('index.html')
    return render_template('register.html')
    
# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/receive', methods=['GET', 'POST'])
def receive():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE uid = %s', [session['uid']])
        account = cursor.fetchone()
        form = ReceiveForm()
        if form.is_submitted():
            result = request.form
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM inventory WHERE blood_type = %s', [result['bloodtype']])
            row = cursor.fetchone()
            # for row in cursor:
            #     print(row)
            return render_template('request.html', result=result, row=row)
        # Show the receive page
        return render_template('receive.html', form=form)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/donate', methods=['GET', 'POST'])
def donate():
        # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            details = request.form
            name = details['name']
            sex = details['sex']
            age = details['age']
            bloodtype = details['bloodtype']
            amount = details['amount']
            address = details['address']
            phone = details['phone']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO donorinfo VALUES (NULL, %s, %s, %s, %s, %s, %s,%s)", (name, sex, age, bloodtype, address, phone, amount))
            mysql.connection.commit()
            cur.close()
            return('You have successfully submitted your donation request')
        return render_template('donate.html')

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    
# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE uid = %s', [session['uid']])
        account = cursor.fetchone()
        form = ReceiveForm()
        return render_template('profile.html', form=form, account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
    
if __name__ == '__main__':
    app.run()