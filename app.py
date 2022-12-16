from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def show_page():
    return render_template('index.html')