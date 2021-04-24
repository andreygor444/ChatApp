from flask import Flask, request, redirect, render_template, jsonify, abort
from flask_login import LoginManager, login_user, login_required, current_user
from datetime import timedelta
import logging

from db_session import db_session_init
from unique_codes_manager import UniqueCodesManager
from temporary_chat_avatars_manager import TemporaryChatAvatarsManager
from unread_messages_manager import UnreadMessagesManager
from config import *
from utils import *
from forms import *


app = Flask(__name__)
app.config["SECRET_KEY"] = "workout"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)

db_session_init(PATH_TO_DB)

login_manager = LoginManager()
login_manager.init_app(app)
unique_codes_manager = UniqueCodesManager()
unique_codes_manager.generate_unique_codes(10)
temporary_chat_avatars_manager = TemporaryChatAvatarsManager()
unread_messages_manager = UnreadMessagesManager()


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
		user = get_user_by_email(form.email.data)
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
		if get_user_by_email(form.email.data, session=db_sess):
			return render_template(
				"register.html",
				form=form,
				message="Пользователь с таким адресом электронной почты уже зарегистрирован"
			)
		add_user(form.name.data, form.surname.data, form.email.data, form.password.data, db_sess)
		return render_template("registered_successfully.html")
	return render_template("register.html", form=form)


@login_required
@app.route("/chats")
def chat_list():
	user_chats = get_user_chats(current_user)
	notifications = current_user.get_notifications_dict()
	user_chats.sort(key=lambda chat: notifications[chat.id], reverse=True)
	user_chats.sort(key=lambda chat: chat.last_message.dispatch_date, reverse=True)
	return render_template("chats.html", user_chats=user_chats)


@login_required
@app.route("/chats/<int:chat_id>")
def chat(chat_id):
	session = create_session()
	try:
		chat = get_chat_by_id(chat_id, session=session)
	except NotFoundError:
		abort(404)
	messages = get_chat_messages(chat_id, sort_param=Message.dispatch_date, session=session)
	unread_messages_manager.reset_unread_messages(current_user.id, chat_id)
	notify_user(current_user.id, chat_id, clear=True, session=session)
	return render_template("chat.html", chat=chat, messages=messages)


@login_required
@app.route("/js/load_temporary_chat_avatar", methods=["PUT"])
def load_temporary_chat_avatar():
	return temporary_chat_avatars_manager.load_avatar(request.data)


@login_required
@app.route("/js/find_user_helper/<user_input>")
def find_user_helper(user_input: str) -> List[User]:
	"""Вызывается когда пользователь ищет другого пользователя,
	принимает те данные, которые ввёл пользователь в поле поиска
	и выдаёт всех пользователей, у которых имя/фамилия/id
	схожи с тем что было введено
	:param user_input: Данные, введённые пользователем
	:returns: Все пользователи, подходящие под запрос
	"""
	db_sess = create_session()
	found_users = set()
	for word in user_input.split():
		if word.isdigit():
			found_users.update(get_users_with_id_like(int(word), session=db_sess))
		found_users.update(get_users_with_name_like(word, session=db_sess))
		found_users.update(get_users_with_surname_like(word, session=db_sess))
	found_users = sorted(found_users, key=lambda user: user.name)
	if current_user in found_users:
		found_users.remove(current_user)
	return jsonify(
		[user.to_dict(only=("id", "name", "surname")) for user in found_users]
	)


@login_required
@app.route("/js/add_chat/<name>/<members>", methods=["POST"])
def add_chat_handler(name, members):
	"""Создаёт чат"""
	creator = current_user.id
	if members == "none":
		members = str(creator)
	else:
		members += f";{creator}"
	session = create_session()
	chat_id = add_chat(name, members, creator, session=session)
	write_first_chat_message(chat_id, current_user.id, session=session)
	chat_avatar = request.data
	if chat_avatar:
		path = os.path.join(PATH_TO_ROOT, "static", "img", "chat_avatars", str(chat_id))
		os.mkdir(path)
		load_image(chat_avatar, f"{path}/avatar.png")
		make_icon(chat_avatar, f"{path}/icon.png")
	for user_id in map(int, members.split(';')):
		add_chat_to_user_chat_list(chat_id, user_id, session=session)
	return jsonify({
		"status": "ok",
		"chat_id": chat_id,
		"creator_id": current_user.id,
		"first_message_text": FIRST_CHAT_MESSAGE_TEXT
	})


@login_required
@app.route("/js/send_message/<int:chat_id>", methods=["POST"])
def send_message(chat_id):
	message_text = request.data.decode()
	session = create_session()
	user_id = current_user.id
	message_id = add_message(user_id, message_text, chat_id, session=session)
	session.query(Chat).filter(Chat.id == chat_id).update({"last_message_id": message_id})
	session.commit()
	chat = get_chat_by_id(chat_id, session=session)
	chat_member_ids = map(int, chat.members.split(';'))
	for member_id in chat_member_ids:
		if member_id != user_id:
			unread_messages_manager.add_unread_message(member_id, chat_id, message_id)
			notify_user(member_id, chat_id, commit=False, session=session)
	session.commit()
	return jsonify({
		"status": "ok",
		"sender_id": user_id,
		"sender_name": current_user.name,
		"sender_surname": current_user.surname
	})


@login_required
@app.route("/js/get_chats_with_unread_messages")
def get_chats_with_unread_messages():
	"""Вызывается клиентом постоянно во время пребывания на странице
	со списком чатов для мониторинга новых сообщений"""
	chats = unread_messages_manager.get_chats_with_unread_messages(current_user.id)
	user_id = current_user.id
	response = {}
	for chat_id, message_ids in chats.items():
		last_message = get_message_by_id(message_ids[-1])
		response[chat_id] = {
			"notifications": len(message_ids),
			"last_message": last_message.to_dict(only=("sender_id", "text", "dispatch_date"))
		}
		unread_messages_manager.reset_unread_messages(user_id, chat_id)
	return jsonify(response)


@login_required
@app.route("/js/get_unread_messages/<int:chat_id>")
def get_unread_messages(chat_id):
	"""Вызывается клиентом постоянно во время пребывания на странице чата
	для мониторинга новых сообщений"""
	message_ids = unread_messages_manager.get_unread_messages(current_user.id, chat_id).copy()
	unread_messages_manager.reset_unread_messages(current_user.id, chat_id)
	messages = get_messages_by_ids(message_ids)
	return jsonify(
		[message.to_dict(only=("sender_id", "sender.name", "sender.surname", "text")) for message in messages]
	)


def main():
	app.run(host="0.0.0.0", port=3838, debug=True)


if __name__ == "__main__":
	main()
