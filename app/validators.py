from wtforms import ValidationError
from string import ascii_letters, digits, punctuation


class PasswordValidator:
    def __init__(self):
        self.letters = set(ascii_letters)
        self.digits = set(digits)
        self.punctuation = set(punctuation)
        self.required_length = 8

    def __call__(self, form, field):
        password = field.data
        if len(password) < self.required_length:
            raise ValidationError("Пароль должен содержать не менее восьми символов")
        password_symbols = set(password)
        if not password_symbols & self.letters:
            raise ValidationError("Пароль должен содержать хотя бы одну латинскую букву")
        if not password_symbols & self.digits:
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        if not password_symbols & self.punctuation:
            raise ValidationError("Пароль должен содержать хотя бы один спецсимвол")


class LengthValidator:
    def __init__(self, min_, max_):
        self.min_ = min_
        self.max_ = max_

    def __call__(self, form, field):
        if len(field.data) < self.min_:
            raise ValidationError(f"Длина этой строки должна быть не менее {self.min_} символов")
        if len(field.data) > self.max_:
            raise ValidationError(f"Длина этой строки не должна превышать {self.max_} символов")
