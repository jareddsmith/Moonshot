import flask

from flask import flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

import json
import logging
import base64

# Date Handling
import arrow
import datetime
from dateutil import tz

# Mongo Database
from pymongo import MongoClient
from bson import ObjectId

#########
#
# GLOBALS
#
#########


import CONFIG

app = flask.Flask(__name__)

print("Entering Setup")

try:
	dbclient = MongoClient(CONFIG.MONGO_URL)
	db = dbclient.classdata
	collection = db.accounts
except:
	print("Failure to open database. Is the Mongo server running? Correct Password?")
	sys.exit(1)

import uuid
app.secret_key = str(uuid.uuid4())

#######
#
# PAGES
#
#######

@app.route("/")
@app.route("/index")
def index():
	app.logger.debug("Main page entry")

	#Clears any saved user data upon returning to the splash page.
	clear_session()
	
	return render_template('splash.html')

@app.route("/signup")
def signup():
	app.logger.debug("Account Creation page entry")
	return render_template('signup.html')

@app.route("/avail")
def avail():
	app.logger.debug("Availability page entry")
	return render_template('avail.html')
	
@app.route("/login")
def login():
	app.logger.debug("Login page entry")
	return render_template('login.html')

@app.route("/dashboard")
def landing():
	app.logger.debug("Dashboard page entry")
	app.logger.debug("Getting accounts now")
	
	accountID = flask.session['user']
	account =  collection.find_one({"_id": ObjectId(accountID)})
	flask.session['first'] = account['first']
	flask.session['last'] = account['last']
	flask.session['email'] = account['email']
	flask.session['avail'] = account['avail']
	flask.session['accounts'] = get_accounts()
	
	return render_template('main.html')
	
@app.route("/user")
def user():
	app.logger.debug("Update account page entry")
	app.logger.debug("Getting account now")
	return render_template('usermenu.html')
	
@app.route("/manage")
def manage():
	app.logger.debug("Manage page entry")
	return render_template('manage.html')

@app.errorhandler(404)
def page_not_found(error):
	app.logger.debug("Page not found")
	return render_template('page_not_found.html', badurl=request.base_url, linkback=url_for("index")), 404

####################
#
# TEMPLATE FUNCTIONS
#
####################

@app.template_filter('humanize')
def humanize_arrow_date(date):
	"""
	Output should be "today", "yesterday", "in X days", etc.
	Arrow will try to humanize down to the minute, so we need to catch 'today'
	as a special case.
	"""

	try:
		then = arrow.get(date).to('local')
		now = arrow.utcnow().to('local')
		if then.date() == now.date():
			human = "Today"
		else:
			human = then.humanize(now)
			if human == "in a day":
				human = "Tomorrow"
	except:
		human = date
	return human

@app.route("/_signup", methods=["POST"])
def create_account():
	"""
	Creates and inserts a new account into the database
	"""
	
	print("Getting account information...")
	first = request.form.get('RegisterFirstNameInput', '', type=str)
	last = request.form.get('RegisterLastNameInput', '', type=str)
	s_id = request.form.get('RegisterIDInput', '', type=str)
	email = request.form.get('RegisterEmailInput', '', type=str)
	pwd = request.form.get('RegisterPasswordInput', '', type=str)
	confirm = request.form.get('LoginRepeatInput', '', type=str)
	
	#Clears any excess whitespace
	first.strip()
	last.strip()
	s_id.strip()
	email.strip()

	print("Testing account information...")
	if signup_errors(first, last, s_id, email, pwd, confirm) == True:
		return redirect("/signup")
	
	print("Encrypting password...")
	pwd = base64.b64encode(pwd.encode('utf-8'))
	flask.session['pwd'] = pwd

	return redirect("/avail")

@app.route("/_avail", methods=["POST"])
def init_avail():
	"""
	Updates new accounts with initial account availability and experience
	"""
	
	first = flask.session['first']
	last = flask.session['last']
	s_id = flask.session['id']
	email = flask.session['email']
	pwd = flask.session['pwd']
	
	#Clears flask variables
	#clear_session()

	#TODO: Pull data from table
	mon_avail = request.form.get('mo', '', type=str)
	tue_avail = request.form.get('tu', '', type=str)
	wed_avail = request.form.get('we', '', type=str)
	thu_avail = request.form.get('th', '', type=str)
	fri_avail = request.form.get('fr', '', type=str)

	print(first)
	print(last)
	print(s_id)
	print(email)
	print(pwd)
	print(mon_avail)
	print(tue_avail)
	print(wed_avail)
	print(thu_avail)
	print(fri_avail)
	
	return redirect("/avail")

@app.route("/_delete")
def delete_account():
	"""
	Deletes accounts by accountID
	"""

	print("Getting account id...")
	accountID = request.args.get('accountID', 0, type=str)
	print("The account ID is " + accountID)
	print("Deleting account...")

	account =  collection.find_one({"_id": ObjectId(accountID)})
	collection.remove(account)
	print("Deleted! Redirecting to **TBD**.")

	return redirect("/**TBD**")
	
@app.route("/_login", methods=["POST"])
def login_user():
	"""
	Logs user in
	"""
	input_email = request.form.get('LoginEmailInput')
	input_pwd = request.form.get('LoginPasswordInput')
	
	account = collection.find_one({"email": input_email})
	print(account)
	if account is None:
		flash("Account not found!")
		return redirect("/login")
	
	pwd = base64.b64decode(account["pwd"]).decode("utf-8")

	if input_pwd == pwd:
		flask.session['user'] =  str(account['_id'])
		
		return redirect("/dashboard")
	else:
		flash("Invalid credentials.")

	if not input_pwd:
		flash("No password entered.")
	
	return redirect("/login")
	
@app.route("/_update", methods=["POST"])
def update_user():
	"""
	Update user information
	"""
	accountID = flask.session['user']
	print(flask.session['first'])
	
	mon = request.form.get('mon', '', type=str)
	tue = request.form.get('tue', '', type=str)
	wed = request.form.get('wed', '', type=str)
	thu = request.form.get('thu', '', type=str)
	fri = request.form.get('fri', '', type=str)
	sat = request.form.get('sat', '', type=str)
	sun = request.form.get('sun', '', type=str)
	avail = mon + tue + wed + thu + fri + sat + sun
	
	first = request.form.get('first', '', type=str)
	last = request.form.get('last', '', type=str)
	major = request.form.get('major', '', type=str)
	email = request.form.get('email', '', type=str)
	phone = request.form.get('phone', '', type=str)
	quote = request.form.get('quote', '', type=str)
	
	if not avail:
		avail = flask.session['avail']		
	if not first:
		first = flask.session['first']
	if not last:
		last = flask.session['last']
	if not major:
		major = flask.session['major']
	if not email:
		email = flask.session['email']
	if not phone:
		phone = flask.session['phone']
	if not quote:
		quote = flask.session['quote']
		
	collection.update({"_id": ObjectId(accountID)},{'$set':{'avail':avail,'first':first,'last':last,'major':major,'email':email,'phone':phone,'quote':quote}})
	flash("Your user information has been updated!")
	return redirect("/dashboard")
	
	
######################
#
# SUPPORTING FUNCTIONS
#
######################

def get_accounts():
	"""
	Returns all accounts in the database, in a form that
	can be inserted directly in the 'session' object.
	"""
	
	print("get_accounts() started.")
	accounts = []
	for account in collection.find({"type" : "account"}):
		account['date'] = arrow.get(account['date']).isoformat()
		account['_id'] = str(account['_id'])
		accounts.append(account)

	accounts.sort(key=lambda a: a["date"])
	return accounts

def insert_new(first, last, s_id, email, pwd, confirm):
	"""
		Inserts an new account into the database with minimum user info
		"""
	date = arrow.utcnow().format('MM/DD/YYYY')
	dt = arrow.get(date, 'MM/DD/YYYY').replace(tzinfo='local')
	iso_dt = dt.isoformat()
	
	#Input checking
	account = collection.find_one({"email": email})
	if account is not None:
		flash("Account already created!")
		return "registered"
	else:
		flash("Account created! You may now login.")
	
	print("Compiling new account from data")
	account = {
		"type" :  "account",
			"role" : "user",
			"date" : iso_dt,
			"first"	: first,
			"last" : last,
			"s_id" : s_id,
			"email" : email,
			"pwd" : pwd,
			"lang" : "",
			"exp" : "",
			"str" : "",
			"wk" : "",
			"avail" : ""
	}

	collection.insert(account)
	print("Account has been inserted into the database.")
	
	return "Success"

def clear_session():
	"""
	Calling this function will clear all of the session variables
	"""

	flask.session['first'] = None
	flask.session['last'] = None
	flask.session['id'] = None
	flask.session['email'] = None
	flask.session['pwd'] = None

	return


def signup_errors(first, last, s_id, email, pwd, confirm):
	"""
	Tests the signup information given for input errors
	"""
	error = False
	
	#First Name Input Error Handling
	if not first:
		flash("No first name given.")
		error = True
	else:
		flask.session['first'] = first
	
	#Last Name Input Error Handling
	if not last:
		flash("No last name given.")
		error = True
	else:
		flask.session['last'] = last

	#Student ID Input Error Handling
	if not s_id:
		flash("No ID given.")
		error = True

	else:
		if s_id.startswith("95") == False:
			flash("ID must begin with 95.")
			error = True

		if len(s_id) != 9:
			flash("ID must be 9 digits.")
			error = True

		else:
			flask.session['id'] = s_id

	#E-mail Input Error Handling
	if not email:
		flash("No email given.")
		error = True
	else:
		flask.session['email'] = email

	#Password Input Error Handling
	if not pwd:
		flash("No password given.")
		error = True

	if pwd != confirm:
		flash("The passwords you entered did not match.")
		error = True

	return error

if __name__ == "__main__":
	app.debug=CONFIG.DEBUG
	app.logger.setLevel(logging.DEBUG)

	if CONFIG.DEBUG:
		# Reachable only from the same computer
		app.run(port=CONFIG.PORT)
	else:
		# Reachable from anywhere
		app.run(port=CONFIG.PORT,host="0.0.0.0")
