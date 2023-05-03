class TokenNotFound(Exception):
    def __init__(self) -> None:
        super().__init__('\n\nОтсутствует токен Яндекс.Музыки.\nПожалуйста, запустите файл get_yandex_token.bat.\n')
