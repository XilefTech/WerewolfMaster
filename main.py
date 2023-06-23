from html import escape
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form["name"].lower()
        return redirect(f"/user/{name}")
    

    return render_template("index.html")

@app.route("/user/<username>")
def userpage(username):
    username = username.capitalize()
    return render_template("user.html", username=escape(username))

while True:
    app.run(host='192.168.178.58', port=80)