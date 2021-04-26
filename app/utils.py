from sqlalchemy.orm import Session
from time import sleep
from threading import Thread
from PIL import Image
from io import BytesIO
from typing import List, Union, Optional, Iterable
import os

from db_session import create_session
from models.user import User
from models.chat import Chat
from config import PATH_TO_ROOT


def async_procedure(func):
	"""Декоратор, позволяющий выполнить процедуру асинхронно"""

	def async_func(*args, **kwargs):
		Thread(target=func, args=args, kwargs=kwargs).start()
	
	return async_func


def delayed_procedure(delay_time):
	"""Декоратор, позволяющий выполнить процедуру асинхронно и с задержкой"""

	def decorator(func):
		@async_procedure
		def delayed_func(*args, **kwargs):
			sleep(delay_time)
			func(*args, **kwargs)

		return delayed_func
	return decorator


def load_image(image: bytes, path: str) -> None:
	with open(path, "wb") as image_file:
		image_file.write(image)


def make_icon(image: Union[str, bytes, BytesIO], path: str) -> None:
	"""Принимает картинку, обрезает её до квадрата и сохраняет"""
	if isinstance(image, bytes):
		image = BytesIO(image)
	image = Image.open(image)
	
	width, height = image.size
	if width > height:
		bias = (width - height) // 2
		image = image.crop((bias, 0, bias + height, height))
	else:
		bias = (height - width) // 2
		image = image.crop((0, bias, width, bias + width))
	image.save(path)


def add_user(name, surname, email, password, session: Optional[Session] = None) -> int:
	if session is None:
		session = create_session()
	user = User()
	user.name = name
	user.surname = surname
	user.email = email
	user.set_password(password)
	session.add(user)
	session.commit()
	return user.id


def edit_user(user: User, name: str, surname: str, avatar: bytes, session: Optional[Session] = None) -> None:
	if session is None:
		session = create_session()
	session.query(User).filter(User.id == user.id).update({"name": name, "surname": surname})
	session.commit()
	if avatar:
		user_avatar_dir = os.path.join(PATH_TO_ROOT, "static", "img", "user_avatars", str(user.id))
		try:
			os.mkdir(user_avatar_dir)
		except FileExistsError:
			pass
		load_image(avatar.read(), os.path.join(user_avatar_dir, "avatar.png"))
		make_icon(avatar, os.path.join(user_avatar_dir, "icon.png"))


def add_chat(name: str, members: Union[Iterable[str], str], creator_id: int, session: Optional[Session] = None) -> int:
	if session is None:
		session = create_session()
	chat = Chat()
	chat.name = name
	if isinstance(members, list):
		members = ';'.join(members)
	chat.members = members
	chat.creator_id = creator_id
	chat.moderators = str(creator_id)
	session.add(chat)
	session.commit()
	return chat.id


def find_user_by_email(email, session: Optional[Session] = None) -> User:
	if session is None:
		session = create_session()
	user = session.query(User).filter(User.email == email).first()
	return user


def get_user_chats(user: User, session: Optional[Session] = None) -> List[Chat]:
	if not user.chats:
		return []
	if session is None:
		session = create_session()
	user_chats_ids = set(map(lambda chat: int(chat.split(':')[0]), user.chats.split(';')))
	user_chats = session.query(Chat).filter(Chat.id.in_(user_chats_ids)).all()
	return user_chats


def find_users_with_id_like(id_fragment: int, session: Optional[Session] = None) -> List[User]:
	"""Ищет пользователей с id, похожим на id_fragment(содержащими его)"""
	if session is None:
		session = create_session()
	return session.query(User).filter(User.id.like(f"%{id_fragment}%")).all()


def find_users_with_name_like(name_fragment: str, session: Optional[Session] = None) -> List[User]:
	"""Ищет пользователей с именами, содержащими name_fragment"""
	if session is None:
		session = create_session()
	return session.query(User).filter(User.name.like(f"%{name_fragment}%")).all()


def find_users_with_surname_like(surname_fragment: str, session: Optional[Session] = None) -> List[User]:
	"""Ищет пользователей с фамилиями, содержащими surname_fragment"""
	if session is None:
		session = create_session()
	return session.query(User).filter(User.surname.ilike(f"%{surname_fragment}%")).all()
