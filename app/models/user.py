import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Dict
import sys

sys.path.append("..")

from db_session import SqlAlchemyBase
from .chat import Chat
from exceptions import NotFoundError


class User(SqlAlchemyBase, UserMixin):
	__tablename__ = "users"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	surname = sqlalchemy.Column(sqlalchemy.String)
	photo = sqlalchemy.Column(sqlalchemy.String, default='default.png')
	email = sqlalchemy.Column(sqlalchemy.String)
	password = sqlalchemy.Column(sqlalchemy.String)
	chats = sqlalchemy.Column(sqlalchemy.String, default='')
	# chats - это строка вида "a1:b1;a2:b2", где a1 и a2 это id чатов,
	# а b1 и b2 - количество непрочитанных сообщений в этих чатах

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def _get_photo_filename_and_extension(self):
		splitted_filename = self.photo.split('.')
		filename = '.'.join(splitted_filename[:-1])
		extension = splitted_filename[-1]
		return filename, extension

	def get_path_to_photo(self):
		filename, extension = self._get_photo_filename_and_extension()
		return f'{filename}/{filename}.{extension}'

	def get_path_to_compressed_photo(self):
		filename, extension = self._get_photo_filename_and_extension()
		return f'{filename}/{filename}_compressed.{extension}'

	def get_path_to_icon(self):
		filename, extension = self._get_photo_filename_and_extension()
		return f'{filename}/{filename}_icon.{extension}'

	def get_notifications_dict(self) -> Dict[int, int]:
		"""Возвращает словарь, в котором ключи - id чатов, а значения - количества непрочитанных сообщений"""
		notifications_dict = {}
		for chat in self.chats.split(';'):
			chat_id, notifications = chat.split(':')
			notifications_dict[int(chat_id)] = int(notifications)
		return notifications_dict

	def get_chat_notifications(self, chat_id: int) -> int:
		"""Возвращает количество не прочитанных пользователем сообщений в чате"""
		chat_id = str(chat_id)
		for id_, notifications in map(lambda chat: chat.split(':'), self.chats.split(';')):
			if id_ == chat_id:
				return int(notifications)
		raise NotFoundError("User is not a member of this chat")

	def add_chat_notification(self, chat: Chat) -> None:
		"""Добавляет к чату в списке чатов пользователя оповещение о непрочитанном сообщении,
		   если пользователь в данный момент не читает этот чат"""
		if self.id not in chat.current_viewers:
			chats = self.chats.split(';')
			chat_id = chat.id
			for i in range(len(chats)):
				id_, unreaded_messages = map(int, chats[i].split(':'))
				if id_ == chat_id:
					chats[i] = f"{id_}:{unreaded_messages + 1}"
					self.chats = ';'.join(chats)
					return
