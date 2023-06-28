from html import escape
from flask import Blueprint, make_response, redirect, render_template, request

from gameData import players

ui = Blueprint('UI', __name__, template_folder='templates', static_folder='static')

@ui.get("/")
def index_get():
	# If the user is already logged in, redirect to the user page
	if request.cookies.get("username"):
		return redirect("/user")
	else:
		return render_template("index.html")


@ui.post("/")
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


@ui.route("/user")
def userpage():
	username = request.cookies.get("username")
	if username:
		if username not in players:
			players.append(username)
		return render_template("user.html", username=escape(username.capitalize()))
	else:
		return redirect("/")


@ui.route("/logout")
def logout():
	name = request.cookies.get("username")
	players.remove(name) if name in players else None

	response = make_response(redirect("/"))
	response.set_cookie("username", "", expires=0)
	return response


@ui.route("/narrator")
def narratorMain():
	return render_template("narrator.html")


@ui.route("/narrator/settings")
def narratorSettings():
	return render_template("settings.html")