from data.users import User


def add_user(db_sess, name, surname, email, password):
	user = User()
	user.name = name
	user.surname = surname
	user.email = email
	user.set_password(password)
	db_sess.add(user)
	db_sess.commit()


def find_user_by_email(db_sess, email):
	user = db_sess.query(User).filter(User.email == email).first()
	return user
