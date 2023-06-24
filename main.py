from html import escape
from flask import Flask, make_response, redirect, render_template, request
from json import dumps

app = Flask(__name__)
players = []
playerTimeout = {}
timeout = 10 # in seconds


@app.get("/")
def index_get():
    # If the user is already logged in, redirect to the user page
    if request.cookies.get("username"):
        return redirect("/user")
    else:
        return render_template("index.html")


@app.post("/")
def index_post():
    # Check entered name and redirect to user page if it is not taken
    name = request.form["name"].lower()
    if name == "":
        return render_template("index.html", error="Please enter a name")

    if name in players:
        return render_template("index.html", error="Name already taken")

    players.append(name)
    # idk maybe you can inject a js/json payload here, but fuck security
    response = make_response(redirect(f"/user"))
    response.set_cookie("username", name)
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
    players.remove(name) if name in players else None

    response = make_response(redirect("/"))
    response.set_cookie("username", "", expires=0)
    return response


@app.route("/narrator")
def narratorMain():
    return render_template("narrator.html")


@app.route("/api")
def api():
    return "<h1>API</h1> <p>If you're seeing this, something probably went wrong because you shouldn't be here.</p>"

@app.route("/api/<path:subpath>")
def api_path(subpath):
    # if a playertimeout is needed, uncomment this, resets the timeout value with every api request
    # if request.cookies.get("username"):
    #     playerTimeout[request.cookies.get("username")] = timeout

    if subpath == "players":
        return dumps(sorted(players))
    return subpath



app.run(host='192.168.178.58', port=80)