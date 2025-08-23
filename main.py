from flask import Flask

app = Flask(__name__)


#TODO: Handle HTML escaping
@app.route('/')
def hello():
    return "<p>hellow</p>"