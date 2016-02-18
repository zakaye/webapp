from app import app, db, lm, ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from flask import render_template, url_for, request, redirect, flash, session, send_from_directory
from flask.ext.login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug import secure_filename
from .forms import Registerform, LoginForm, UploadForm
from .user import User
import os
import datetime

def allowed_file(filename):
	return "." in filename and \
		filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS
		
def wronguser(username):
	if username == session['username']:
		return False
	else:
		return True

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
	elif wronguser(username):
		return render_template("invalid.html")
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
		return render_template("invalid.html")
		
@app.route('/logout')
@login_required
def logout():
	logout_user()
	session.pop('username', None)
	flash("You were logged out", category='success')
	return redirect(url_for('main'))
	
@app.route('/list/<username>')
@login_required
def list(username):
	if wronguser(username):
		return render_template("invalid.html")
	else:
		if db.uploads.find({'username':username}).count() == 0:
			result = False
			return render_template("list.html", result = result)
		else:
			result = db.uploads.find({'username':username})
			return render_template("list.html", result = result)
	
@app.route('/upload/<username>', methods=['GET', 'POST'])
@login_required
def upload(username):
	if wronguser(username):
		return render_template("invalid.html")
	else:
		form = UploadForm()
		if request.method == 'POST':
			file = request.files['file']
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				filename = username + "_" + filename
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				db.uploads.insert({'username':username, 'filename':filename, 'date':datetime.datetime.now(), 'location':os.path.join(app.config['UPLOAD_FOLDER'], filename), 'permission':1})
				flash('File Uploaded', category='success')
		return render_template("upload.html", form = form)
	
@app.route('/download/<filename>')
@login_required
def download(username, filename):
	if wronguser(username):
		return render_template("invalid.html")
	else:
		correct = db.uploads.find_one({"filename":filename})
		if correct['username'] == username & correct['permission'] == 1:
			return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
		else:
			return render_template("invalid.html")
	
@lm.user_loader
def load_user(username):
    u = db.users.find_one({"username": username})
    if not u:
        return None
    return User(u['_id'])