from sqlalchemy.orm import Session
from typing import List

from models.user import User
from models.chat import Chat


def add_user(db_sess: Session, name, surname, email, password) -> None:
	user = User()
	user.name = name
	user.surname = surname
	user.email = email
	user.set_password(password)
	db_sess.add(user)
	db_sess.commit()


def find_user_by_email(db_sess: Session, email) -> User:
	user = db_sess.query(User).filter(User.email == email).first()
	return user


def get_user_chats(db_sess: Session, user: User) -> List[Chat]:
	if not user.chats:
		return []
	user_chats_ids = set(map(lambda chat: int(chat.split(':')[0]), user.chats.split(';')))
	user_chats = db_sess.query(Chat).filter(Chat.id.in_(user_chats_ids)).all()
	return user_chats
