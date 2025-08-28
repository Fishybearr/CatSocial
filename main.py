import os

from flask import Flask, render_template, request, make_response, redirect,flash, url_for
import mariadb
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

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
app.secret_key = 'temp secret key' #TODO: randomly generate this

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#TODO: Handle HTML escaping
@app.route('/')
def hello():
    cook = request.cookies.get('username')
    if cook == "testName":
        return render_template('LoggedInFeed.html')
    return render_template('index.html')


#TODO REMOVE THIS
@app.route('/user/<int:userID>')
def displayUserHome(userID):
    return f"some user home {userID}"


"""Displays and processes login form"""
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    cook = request.cookies.get('username')
    if cook == "testName":
        return '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:5000/">" />'



    if request.method == 'POST':
        uname = request.form.get('uname')
        psswd = request.form.get('psswd')

        try:
            conn = mariadb.connect(**db_config)
            print("Connected to MariaDB successfully!")
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")

        cursor = conn.cursor()
        #TODO: Modify this to sanatize input and then check if it's
        #in the DB.
        cursor.execute(f"SELECT * FROM users WHERE username = '{uname}'")

        row = cursor.fetchone()

        #Check if the username is in the DB and then validate
        #password hash (hashing not implemented yet)
        #TODO: Implement hashing function here
        if row != None and row[2] == psswd:
            resp = make_response('<meta http-equiv="refresh" content="0; url=http://127.0.0.1:5000/">" />')
            resp.set_cookie('username', 'testName', secure=True, max_age=3600) #TODO: enable httponly and esnure that js can stil send the cookie
            return resp

            #Eventually will send a cookie here and store it
            #in the DB, then give access to custom feed page
        else:
            return f"invalid login"
        cursor.close()

    return render_template('login.html')


#TODO: Secure the file upload and info validation systems further
@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        #process form image
        if 'profilePic' not in request.files:
            return redirect(request.url)

        profilePic = request.files['profilePic']

        if profilePic.filename == '':
            return redirect(request.url)

        fn = secure_filename(profilePic.filename)
        profilePic.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))

        #save this filepath to the DB with the user
        #TODO: set image size constraints for uploading
        #TODO: verifiy username is not in use when user submits

        #process from text
        uname = request.form.get('uname')
        psswd = request.form.get('psswd')
        cat_name = request.form.get('cat_name')

        try:
            conn = mariadb.connect(**db_config)
            print("Connected to MariaDB successfully!")
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB: {e}")

        #send the account info to the DB
        cursor = conn.cursor()

        #check if username is already in use
        cursor.execute(f"SELECT * FROM users WHERE username = '{uname}'")
        row = cursor.fetchone()
        if row != None:
            cursor.close()
            conn.close()
            flash("username already in use")
            return redirect(url_for('createAccount'))



        cursor.execute(f"INSERT INTO users (username,cat_name,password_hash,profile_picture_path) VALUES('{uname}','{cat_name}','{psswd}','testPath')")
        conn.commit()
        cursor.close()
        conn.close()

        #assign cookie to user and redirect them to their main feed upon successful login
        resp = make_response('<meta http-equiv="refresh" content="0; url=http://127.0.0.1:5000/">" />') #TODO: swap these for redirects
        resp.set_cookie('username', 'testName', secure=True,max_age=3600)  # TODO: enable httponly and esnure that js can stil send the cookie
        return resp

        #return f"<p> catname: {cat_name}\n username: {uname} password: {psswd}</p>"

    return render_template('CreateAccount.html')


"""
@app.route('/random', methods = ['GET', 'POST'])
def random():

    #This will set the cookie for the user and then redirect them to the home page
    resp = make_response('<meta http-equiv="refresh" content="0; url=http://127.0.0.1:5000/">" />')
    resp.set_cookie('username','testName')
    return resp
"""

if __name__ == '__main__':
    app.run(debug=True)