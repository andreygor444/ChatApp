from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from time import sleep
from threading import Thread
from PIL import Image
from io import BytesIO
from typing import List, Union, Optional, Iterable
import datetime
import logging

from db_session import create_session
from models.user import User
from models.chat import Chat
from models.message import Message
from config import FIRST_CHAT_MESSAGE_TEXT
from exceptions import *


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


def load_image(image: bytes, path) -> None:
    with open(path, "wb") as image_file:
        image_file.write(image)


def make_icon(image: Union[str, bytes, BytesIO], path) -> None:
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


def get_chat_by_id(chat_id: int, session: Optional[Session] = None) -> Chat:
    if session is None:
        session = create_session()
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    if chat is None:
        raise NotFoundError(f"Chat with id {chat_id} not found")
    return chat


def get_chat_messages(chat: Union[int, Chat], sort_param: Optional[InstrumentedAttribute] = None,
                      session: Optional[Session] = None) -> List[Message]:
    if session is None:
        session = create_session()
    if isinstance(chat, Chat):
        chat = chat.id
    return session.query(Message).filter(Message.chat_id == chat).order_by(sort_param).all()


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


def add_chat(name: str, members: Union[Iterable[str], str], creator_id: int, session: Optional[Session] = None) -> int:
    if session is None:
        session = create_session()
    chat = Chat()
    chat.name = name
    if isinstance(members, list):
        members = ';'.join(map(str, members))
    chat.members = members
    chat.creator_id = creator_id
    session.add(chat)
    session.commit()
    return chat.id


def edit_chat(chat_id: int, chat_name: str, members: Union[Iterable[str], str], session: Optional[Session] = None) -> List[List[int]]:
    if session is None:
        session = create_session()
    if isinstance(members, list):
        members_set = set(map(int, members))
        members = ';'.join(map(str, members))
    else:
        members_set = set(map(int, members.split(';')))
    
    chat = session.query(Chat).filter(Chat.id == chat_id).first()
    current_members = set(map(int, chat.members.split(';')))
    new_members = members_set - current_members
    deleted_members = current_members - members_set
    
    session.query(Chat).filter(Chat.id == chat_id).update({"name": chat_name, "members": members})
    session.commit()
    return tuple(new_members), tuple(deleted_members)


def add_message(sender_id: int, message_text: str, chat_id: int, session: Optional[Session] = None) -> int:
    if session is None:
        session = create_session()
    message = Message()
    message.sender_id = sender_id
    message.dispatch_date = datetime.datetime.now()
    message.text = message_text
    message.chat_id = chat_id
    session.add(message)
    session.commit()
    return message.id


def write_first_chat_message(chat_id: int, user_id: int, session: Optional[Session] = None) -> Message:
    if session is None:
        session = create_session()
    message = Message()
    message.sender_id = user_id
    message.dispatch_date = datetime.datetime.now()
    message.text = FIRST_CHAT_MESSAGE_TEXT
    message.chat_id = chat_id
    session.add(message)
    session.commit()
    session.query(Chat).filter(Chat.id == chat_id).update({"last_message_id": message.id})
    session.commit()
    return message


def get_user_by_id(user_id: int, session: Optional[Session] = None) -> User:
    if session is None:
        session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    return user


def get_user_by_email(email: str, session: Optional[Session] = None) -> User:
    if session is None:
        session = create_session()
    user = session.query(User).filter(User.email == email).first()
    return user


def notify_user(user_id: int, chat_id: int, clear=False, commit=True, session: Optional[Session] = None) -> None:
    if session is None:
        session = create_session()
    user = get_user_by_id(user_id, session=session)
    notifications = user.get_notifications_dict()
    try:
        if clear:
            notifications[chat_id] = 0
        else:
            notifications[chat_id] += 1
        notifications = ';'.join(':'.join(map(str, item)) for item in notifications.items())
        session.query(User).filter(User.id == user_id).update({"chats": notifications})
        if commit:
            session.commit()
    except KeyError:
        logging.warning("Пользователь не состоит в чате, из которого ему пришло сообщение!")


def get_user_chats(user: User, session: Optional[Session] = None) -> List[Chat]:
    if not user.chats:
        return []
    if session is None:
        session = create_session()
    user_chats_ids = set(map(lambda chat: int(chat.split(':')[0]), user.chats.split(';')))
    user_chats = session.query(Chat).filter(Chat.id.in_(user_chats_ids)).all()
    return user_chats


def get_users_with_id_like(id_fragment: int, session: Optional[Session] = None) -> List[User]:
    """Ищет пользователей с id, похожим на id_fragment(содержащими его)"""
    if session is None:
        session = create_session()
    return session.query(User).filter(User.id.like(f"%{id_fragment}%")).all()


def get_users_with_name_like(name_fragment: str, session: Optional[Session] = None) -> List[User]:
    """Ищет пользователей с именами, содержащими name_fragment"""
    if session is None:
        session = create_session()
    return session.query(User).filter(User.name.like(f"%{name_fragment}%")).all()


def get_users_with_surname_like(surname_fragment: str, session: Optional[Session] = None) -> List[User]:
    """Ищет пользователей с фамилиями, содержащими surname_fragment"""
    if session is None:
        session = create_session()
    return session.query(User).filter(User.surname.ilike(f"%{surname_fragment}%")).all()


def add_chat_to_user_chat_list(chat_id: int, user_id: int, session: Optional[Session] = None) -> None:
    if session is None:
        session = create_session()
    user = session.query(User).filter(User.id == user_id).first()
    if user.chats:
        user.chats += ';'
    user.chats += f"{chat_id}:1"
    session.commit()


def get_message_by_id(message_id: int, session: Optional[Session] = None) -> Message:
    if session is None:
        session = create_session()
    return session.query(Message).filter(Message.id == message_id).first()


def get_messages_by_ids(message_ids: Iterable, session: Optional[Session] = None) -> List[Message]:
    if session is None:
        session = create_session()
    return session.query(Message).filter(Message.id.in_(message_ids)).all()
