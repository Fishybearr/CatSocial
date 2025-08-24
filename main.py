from os import uname

from flask import Flask, render_template, request
import mariadb

#TODO This are test credentials that will be disabled in production
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'test_user',
    'password': 'test_pass',
    'database': 'cat_social'
    }

try:
    conn = mariadb.connect(**db_config)
    print("Connected to MariaDB successfully!")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB: {e}")

app = Flask(__name__)


#TODO: Handle HTML escaping
@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/user/<int:userID>')
def displayUserHome(userID):
    return f"some user home {userID}"


"""Displays and processes login form"""
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        uname = request.form.get('uname')
        psswd = request.form.get('psswd')
        cursor = conn.cursor()
        #TODO: Modify this to sanatize input and then check if it's
        #in the DB.
        cursor.execute(f"SELECT * FROM users WHERE username = '{uname}'")

        row = cursor.fetchone()

        #currently only fetching the first row of the db
        #in the future we search the db for the username and then
        #validate the password
        if row != None and row[1] == uname and row[2] == psswd:
            return f"{uname},{psswd},{row}"
        else:
            return f"invalid login"
        cursor.close()

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
