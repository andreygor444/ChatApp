from flask import Flask, request, redirect, render_template, jsonify, abort
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from db_session import db_session_init
from unique_codes_manager import UniqueCodesManager
from temporary_chat_avatars_manager import TemporaryChatAvatarsManager
from config import *
from utils import *
from forms import *


app = Flask(__name__)
app.config["SECRET_KEY"] = "workout"

db_session_init(PATH_TO_DB)

login_manager = LoginManager()
login_manager.init_app(app)
unique_codes_manager = UniqueCodesManager()
unique_codes_manager.generate_unique_codes(10)
temporary_chat_avatars_manager = TemporaryChatAvatarsManager()


@login_required
@app.route('/logout')
def logout_user():
    logout_user()
    return redirect('/')


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
        user = find_user_by_email(form.email.data)
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
        if find_user_by_email(form.email.data, session=db_sess):
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
    db_sess = create_session()
    user_chats = get_user_chats(current_user, session=db_sess)
    user_chats.sort(key=lambda chat: chat.last_message.dispatch_date)
    notifications = current_user.get_notifications_dict()
    user_chats.sort(key=lambda chat: notifications[chat.id], reverse=True)
    return render_template("chats.html", user_chats=user_chats)


@login_required
@app.route("/profile", methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
        photo = os.path.join(PATH_TO_ROOT, 'static/img/chat_avatars/default/avatar.png')
        if os.path.isfile('static/img/user_avatars/' + str(current_user.id) + '/avatar.png'):
            photo = os.path.join(PATH_TO_ROOT, 'static', 'img', 'chat_avatars', str(current_user.id), 'avatar.png')
        notifications = current_user.get_notifications_dict()
        all_not = sum([int(i.split(':')[1]) for i in notifications])
        user = {
            'photo': photo,
            'name': current_user.name,
            'surname': current_user.surname,
            'notifications': str(all_not)
        }
        return render_template("profile.html", user=user)
    elif request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        file = request.files.get('file')
        change_user_in_profile(current_user, name, surname, file)
        return redirect('/profile')


@app.errorhandler(404)
def error_404(error):
    return render_template("404.html")


@app.route("/js/load_unique_link")
def get_unique_code():
    return unique_codes_manager.get_unique_code()


@app.route("/js/load_temporary_chat_avatar", methods=["PUT"])
def load_temporary_chat_avatar():
    return temporary_chat_avatars_manager.load_avatar(request.data)


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
            found_users.update(find_users_with_id_like(int(word), session=db_sess))
        else:
            found_users.update(find_users_with_name_like(word, session=db_sess))
            found_users.update(find_users_with_surname_like(word, session=db_sess))
    found_users = sorted(found_users, key=lambda user: user.name)
    if current_user in found_users:
        found_users.remove(current_user)
    return jsonify(
        [user.to_dict(only=("id", "name", "surname")) for user in found_users]
    )


@app.route("/js/add_chat/<name>/<members>", methods=["POST"])
def add_chat_handler(name, members):
    """Создаёт чат"""
    creator = current_user.id
    if members == "none":
        members = str(creator)
    else:
        members += f";{creator}"
    chat_id = add_chat(name, members, creator)
    chat_avatar = request.data
    if chat_avatar:
        path = os.path.join(PATH_TO_ROOT, "static", "img", "chat_avatars", str(chat_id))
        os.mkdir(path)
        load_image(chat_avatar, f"{path}/avatar.png")
        make_icon(chat_avatar, f"{path}/icon.png")
    return jsonify({"status": "ok"})


def main():
    app.run(host="127.0.0.1", port=8080, debug=True)


if __name__ == "__main__":
    main()
