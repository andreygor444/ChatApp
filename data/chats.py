import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase):
	__tablename__ = "chats"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	members = sqlalchemy.Column(sqlalchemy.String, default='')
	creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
	last_message_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("messages.id"))
	moderators = sqlalchemy.Column(sqlalchemy.String, default='')
	unique_code = sqlalchemy.Column(sqlalchemy.String)
	current_viewers = sqlalchemy.Column(sqlalchemy.String, default='')  # Пользователи, просматривающие чат в данный момент
	creator = orm.relation("User")
	last_message = orm.relation("Message", foreign_keys=[last_message_id])
