from collections import defaultdict
from typing import List, Dict


class UnreadMessagesManager:
    """Класс, отвечающий за получение пользователями сообщений.
    Клиенты обращаются к серверу, чтобы получить новые сообщения,
    а сервер обращается к этому классу, чтобы вернуть клиентам
    эти сообщения"""

    def __init__(self):
        self._unread_messages = defaultdict(lambda: defaultdict(list))
        # Это будет словарь вида {user_id: {chat_id: [message_1_id, message_2_id, ...]}}.
        # В нём будут храниться непрочитанные сообщения пользователей из различных чатов

    def add_unread_message(self, user_id, chat_id, message_id):
        self._unread_messages[user_id][chat_id].append(message_id)    

    def get_chats_with_unread_messages(self, user_id) -> Dict[int, List[int]]:
        return {chat: messages for chat, messages in self._unread_messages[user_id].items() if messages}
    
    def get_unread_messages(self, user_id, chat_id) -> List[int]:
        return self._unread_messages[user_id][chat_id]
    
    def reset_unread_messages(self, user_id, chat_id):
        self._unread_messages[user_id][chat_id].clear()
