class ValutaTradeError(Exception):
    #базовый класс для всех ошибок приложения
    pass

class CurrencyNotFoundError(ValutaTradeError):
    #когда валюта не найдена в реестре
    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        super().__init__(f"Валюта '{currency_code}' не найдена в системе.")

class InsufficientFundsError(ValutaTradeError):
    #когда не хватает денег
    pass