from html import escape
from flask import Blueprint, make_response, redirect, render_template, request
import time

import gameData

from . import ui
from main import socketio
# ui = Blueprint('UI', __name__, template_folder='templates', static_folder='static')

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

	if name in gameData.players and request.form["forceJoin"].lower() != "true":
		return render_template("indexRejoin.html", error="Name already taken")
	
	if request.form["forceJoin"].lower() != "true":
		gameData.players.append(name)
	
	response = make_response(redirect(f"/user"))
	response.set_cookie("username", name)
	return response


@ui.route("/user")
def userpage():
	username = request.cookies.get("username")
	if username:
		if username not in gameData.players:
			gameData.players.append(username)
		return render_template("user.html", username=escape(username.capitalize()))
	else:
		return redirect("/")


@ui.route("/logout")
def logout():
	name = request.cookies.get("username")
	gameData.players.remove(name) if name in gameData.players else None

	response = make_response(redirect("/"))
	response.set_cookie("username", "", expires=0)
	return response


@ui.route("/narrator")
def narratorMain():
	return render_template("narrator.html")


@ui.route("/narrator/settings")
def narratorSettings():
	return render_template("settings.html")

@ui.route("/narrator/story")
def narratorStory():
	return render_template("narratorNightProg.html")