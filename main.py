from flask import Flask, redirect, render_template
from flask_login import LoginManager, login_user, login_required

from data.db_session import db_session_init, create_session
from data.users import User
from data.chats import Chat
from data.messages import Message

from forms import *
from utils import *


app = Flask(__name__)
app.config['SECRET_KEY'] = 'workout'
db_session_init("db/main.db")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
	return create_session().query(User).get(user_id)


@login_required
@app.route('/')
def home_page():
	return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def authorization():
	form = LoginForm()
	if form.validate_on_submit():
		user = find_user_by_email(create_session(), form.email.data)
		if user and user.check_password(form.password.data):
			login_user(user, remember=form.remember_me.data)
			return redirect('/')
		return render_template("login.html",
			message="Неправильный логин или пароль",
			form=form)
	return render_template("login.html", form=form)


def main():
	app.run(host='0.0.0.0', port=4444, debug=True)


if __name__ == '__main__':
	main()
