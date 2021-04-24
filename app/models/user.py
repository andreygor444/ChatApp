import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from typing import Dict
import sys

sys.path.append("..")

from db_session import SqlAlchemyBase
from .chat import Chat
from exceptions import NotFoundError


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
	__tablename__ = "users"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	surname = sqlalchemy.Column(sqlalchemy.String)
	email = sqlalchemy.Column(sqlalchemy.String)
	password = sqlalchemy.Column(sqlalchemy.String)
	chats = sqlalchemy.Column(sqlalchemy.String, default='')
	# chats - это строка вида "a1:b1;a2:b2", где a1 и a2 это id чатов,
	# а b1 и b2 - количество непрочитанных сообщений в этих чатах

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def get_notifications_dict(self) -> Dict[int, int]:
		"""Возвращает словарь, в котором ключи - id чатов, а значения - количества непрочитанных сообщений"""
		if not self.chats:
			return {}
		notifications_dict = {}
		for chat in self.chats.split(';'):
			chat_id, notifications = chat.split(':')
			notifications_dict[int(chat_id)] = int(notifications)
		return notifications_dict

	def get_chat_notifications(self, chat_id: int) -> int:
		"""Возвращает количество не прочитанных пользователем сообщений в чате"""
		if not self.chats:
			raise NotFoundError("User is not a member of any chat")
		chat_id = str(chat_id)
		for id_, notifications in map(lambda chat: chat.split(':'), self.chats.split(';')):
			if id_ == chat_id:
				return int(notifications)
		raise NotFoundError("User is not a member of this chat")

	def add_chat_notification(self, chat: Chat) -> None:
		"""Добавляет к чату в списке чатов пользователя оповещение о непрочитанном сообщении"""
		chats = self.chats.split(';')
		chat_id = chat.id
		for i in range(len(chats)):
			id_, unread_messages = map(int, chats[i].split(':'))
			if id_ == chat_id:
				chats[i] = f"{id_}:{unread_messages + 1}"
				self.chats = ';'.join(chats)
				return
