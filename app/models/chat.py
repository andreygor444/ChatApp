import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import Session
from typing import List, Optional
import sys

sys.path.append("..")

from db_session import SqlAlchemyBase, create_session
from .user import User


class Chat(SqlAlchemyBase):
	__tablename__ = "chats"

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	members = sqlalchemy.Column(sqlalchemy.String)
	creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
	last_message_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("messages.id"))
	moderators = sqlalchemy.Column(sqlalchemy.String)
	creator = orm.relation("User")
	last_message = orm.relation("Message", foreign_keys=[last_message_id])

	def get_members(self, session: Optional[Session] = None) -> List[User]:
		if session is None:
			session = create_session()
		members = set(map(int, self.members.split(';')))
		return session.query(User).filter(User.id.in_(members)).all()
