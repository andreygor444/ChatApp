import sqlalchemy

from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase):
	__tablename__ = "chats"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	members = sqlalchemy.Column(sqlalchemy.String)
	creator_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"))
	moderators = sqlalchemy.Column(sqlalchemy.String)
	unique_code = sqlalchemy.Column(sqlalchemy.String)
	creator = sqlalchemy.orm.relation('User')
