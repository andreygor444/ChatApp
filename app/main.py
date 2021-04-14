from flask import Flask, redirect, render_template, abort
from flask_login import LoginManager, login_user, login_required, current_user
import inspect
import os

from db_session import db_session_init, create_session
from unique_codes_manager import UniqueCodesManager
from forms import *
from utils import *


app = Flask(__name__)
app.config["SECRET_KEY"] = "workout"

current_file = inspect.getframeinfo(inspect.currentframe()).filename
path_to_current_file = os.path.dirname(os.path.abspath(current_file))
path_to_db = os.path.join(path_to_current_file, "db/main.db")
db_session_init(path_to_db)

login_manager = LoginManager()
login_manager.init_app(app)
unique_codes_manager = UniqueCodesManager()
unique_codes_manager.generate_unique_codes(10)


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
		return render_template("login.html", message="Неправильный логин или пароль", form=form)
	return render_template("login.html", form=form)


@app.route("/register/<unique_code>", methods=["GET", "POST"])
def registration(unique_code):
	if not unique_codes_manager.check_code(unique_code):
		abort(403)
	#unique_codes_manager.update_code(unique_code)
	form = RegisterForm()
	if form.validate_on_submit():
		db_sess = create_session()
		if find_user_by_email(db_sess, form.email.data):
			return render_template("register.html", form=form, message="Пользователь с таким адресом электронной почты уже зарегистрирован")
		add_user(db_sess, form.name.data, form.surname.data, form.email.data, form.password.data)
		return render_template("registered_successfully.html")
	return render_template("register.html", form=form)


@login_required
@app.route("/chats")
def chat_list():
	db_sess = create_session()
	user_chats = get_user_chats(db_sess, current_user)
	user_chats.sort(key=lambda chat: chat.last_message.dispatch_date)
	notifications = current_user.get_notifications_dict()
	print(notifications)
	user_chats.sort(key=lambda chat: notifications[chat.id], reverse=True)
	return render_template("chats.html", user_chats=user_chats)


def main():
	app.run(host="0.0.0.0", port=3838, debug=True)


if __name__ == "__main__":
	main()
