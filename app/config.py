import inspect
import os


current_file = inspect.getframeinfo(inspect.currentframe()).filename

DB_FILE = "db/main.db"
PATH_TO_ROOT = os.path.dirname(os.path.abspath(current_file))
PATH_TO_DB = os.path.join(PATH_TO_ROOT, DB_FILE)
FIRST_CHAT_MESSAGE_TEXT = "Чат создан."
