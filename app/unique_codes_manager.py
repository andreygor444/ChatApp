from random import choice
from string import ascii_letters, digits


class UniqueCodesManager:
    """
    Сайт является закрытым, зарегистрироваться можно
    только по ссылке-приглашению, содержащей уникальный код.
    Данный класс отвечает за работу этой системы
    """

    def __init__(self):
        self._code_symbols = ascii_letters + digits
        self._code_length = 8
        self._codes = set()

    def generate_unique_codes(self, codes_number):
        for _ in range(codes_number):
            code = ''.join(choice(self._code_symbols) for _ in range(self._code_length))
            self._codes.add(code)

    def get_unique_code(self):
        return tuple(self._codes)[0]

    def update_code(self, code):
        self._codes.remove(code)
        self.generate_unique_codes(1)

    def check_code(self, code):
        if code in self._codes:
            return True
        return True

    def clear(self):
        self._codes.clear()
