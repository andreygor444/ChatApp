from multiprocessing import Value
import os

from config import *
from utils import delayed_procedure, make_icon


class TemporaryChatAvatarsManager:
    """В директории static/img/temporary_chat_avatars хранятся аватары чатов,
    которые выбирают пользователи на этапе создания чата, не создавая при этом чат окончательно.
    Эти фотографии сохраняются и через 10 секунд удаляются.
    Данный менеджер управляет этим процессом."""

    def __init__(self):
        self.dir = os.path.join(PATH_TO_ROOT, "static", "img", "temporary_chat_avatars")
        # Директория, в которой хранятся временные аватары
        self.files_counter = Value('i', 0)
        # Имя временного файла будет соответствовать его порядковому номеру, для этого нужен счётчик
        self.released_values = []
        # В этом списке будут лежать отработанные значения счётчика
        self.clear_temporary_chat_avatars_dir()
    
    def clear_temporary_chat_avatars_dir(self):
        for file in os.listdir(self.dir):
            if not file.endswith(".md"):
                os.remove(os.path.join(self.dir, file))

    def load_avatar(self, data: bytes) -> str:
        """Сохраняет файл, переданный пользователем, сжимая его до размера 200x200,
        и возвращает относительный путь до него"""
        with self.files_counter.get_lock():
            self.files_counter.value += 1
            current_value = self.files_counter.value
        filename = f"{self.files_counter.value}.png"
        path_to_avatar = os.path.join(self.dir, filename)
        make_icon(data, path_to_avatar)
        self.delete_avatar(path_to_avatar, current_value)
        return os.path.relpath(path_to_avatar, "app")
    
    @delayed_procedure(10)
    def delete_avatar(self, path_to_avatar, value):
        """Удаляет аватар и освобождает имя, отданное этому аватару"""
        os.remove(path_to_avatar)    
        self.release_value(value)
    
    def release_value(self, value):
        """Помещает значение счётчика в список отработанных и откатывает счётчик файлов насколько это возможно"""
        self.released_values.append(value)
        for released_value in reversed(self.released_values):
            if self.files_counter.value == released_value + 1:
                with self.files_counter.get_lock():
                    self.files_counter.value -= 1
                try:
                    self.released_values.pop()
                except IndexError:
                    continue
