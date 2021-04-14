import sqlalchemy
from sqlalchemy import orm
import sys

sys.path.append("..")

from db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
	__tablename__ = "messages"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	sender_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"))
	dispatch_date = sqlalchemy.Column(sqlalchemy.DateTime)
	text = sqlalchemy.Column(sqlalchemy.Text)
	chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"))
	sender = orm.relation("User")
	chat = orm.relation("Chat", foreign_keys=[chat_id])

	def get_dispatch_date_for_html(self):
		return self.dispatch_date.strftime("%Y-%m-%d %H:%M").split()
