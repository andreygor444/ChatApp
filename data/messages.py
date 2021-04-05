import sqlalchemy

from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
	__tablename__ = "messages"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	sender_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"))
	dispatch_date = sqlalchemy.Column(sqlalchemy.DateTime)
	unique_code = sqlalchemy.Column(sqlalchemy.String)
	text = sqlalchemy.Column(sqlalchemy.Text)
	chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("chats.id"))
	sender = sqlalchemy.orm.relation("User")
	chat = sqlalchemy.orm.relation("Chat")
