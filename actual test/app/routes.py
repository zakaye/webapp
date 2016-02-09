from app import app, db, lm
from flask import render_template, url_for, request, redirect, flash, session
from flask.ext.login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import Registerform, LoginForm
from .user import User

@app.route('/', methods=['GET','POST'])
def main():
	form = LoginForm()
	if 'username' in session:
		return redirect(url_for('user', username = session['username']))
	if form.validate_on_submit():
		if db.users.find({'username':form.username.data}).count() == 0:
			flash('Username does not exist', category='error')
		else:
			correct = db.users.find_one({"username":form.username.data})
			if check_password_hash(correct['password'], form.password.data):
				user = User(form.username.data)
				#session['ident'] = correct['_id']
				session['username'] = form.username.data
				login_user(user)
				return redirect(request.args.get("next") or url_for('user', username = form.username.data) )
			flash('Wrong Password', category='error')
	test = "Login"
	return render_template("index.html", form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	if username == None:
		return redirect(url_for('main'))
	elif db.users.find({'username':username}).count() == 0:
		return redirect(url_for('register'))
	elif session['username'] != username:
		return "Invalid"
	else:
		curuser = db.users.find_one({"username":username})
		return render_template("dash.html", user = curuser['username'], email = curuser['email'])
	
@app.route('/register', methods=['GET','POST'])
def register():
	form = Registerform()
	if request.method == "GET":
		return render_template("register.html", form=form)
	elif request.method == "POST":
		if form.password.data != form.password2.data:
			flash('Passwords does not match', category='error')
			return render_template("register.html", form=form)
		elif db.users.find({"username": form.username.data}).count() != 0:
			flash('Username already in use', category='error')
			return render_template("register.html", form=form)
		else:
			pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
			db.users.insert({'username':form.username.data, 'email':form.email.data, 'password':pw})
			user = User(form.username.data)
			login_user(user)
			flash('Its working', category='success')
			return redirect(request.args.get("next") or url_for('user', username = form.username.data))
	else:
		return "<h2>Invalid</h2>"
		
@app.route('/logout')
@login_required
def logout():
	logout_user()
	session.pop('username', None)
	flash("You were logged out", category='success')
	return redirect(url_for('main'))
	
@lm.user_loader
def load_user(username):
    u = db.users.find_one({"username": username})
    if not u:
        return None
    return User(u['_id'])