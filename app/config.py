import inspect
import os


current_file = inspect.getframeinfo(inspect.currentframe()).filename

DB_FILE = "db/main.db"
HOST = "127.0.0.1"
PORT = 8080
PATH_TO_ROOT = os.path.dirname(os.path.abspath(current_file))
PATH_TO_DB = os.path.join(PATH_TO_ROOT, DB_FILE)
FIRST_CHAT_MESSAGE_TEXT = "Чат создан."
