from html import escape
from flask import Flask, make_response, redirect, render_template, request

app = Flask(__name__)
players = []

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form["name"].lower()
        if name not in players:
            players.append(name)
            
            response = make_response(redirect(f"/user"))
            response.set_cookie("username", name)
            return response
        else:
            return render_template("index.html", error="Name already taken")
    
    name = request.cookies.get("username")
    players.remove(name) if name in players else None

    response = make_response(render_template("index.html"))
    response.set_cookie("username", "", expires=0)
    return response

@app.route("/user")
def userpage():
    username = request.cookies.get("username")
    if username:
        return render_template("user.html", username=escape(username.capitalize()))
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    name = request.cookies.get("username")
    players.remove(name)

    response = make_response(redirect("/"))
    response.set_cookie("username", "", expires=0)
    return response

@app.route("/narrator")
def narratorMain():
    return render_template("narrator.html")

while True:
    app.run(host='192.168.178.58', port=80)