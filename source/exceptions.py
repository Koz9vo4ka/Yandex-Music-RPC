class TokenNotFound(Exception):
    def __init__(self) -> None:
        super().__init__("""
        Отсутствует токен Яндекс.Музыки.
        Пожалуйста, запустите файл get_yandex_token.bat.
        """)
