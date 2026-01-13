from abc import ABC, abstractmethod
from typing import Dict
from valutatrade_hub.core.exceptions import CurrencyNotFoundError

class Currency(ABC):
    def __init__(self, code: str, name: str):
        #валидация кода
        if not code or len(code) < 2 or len(code) > 5:
            raise ValueError(f"Некорректная длина кода валюты: {code}")
        if not code.isupper():
            raise ValueError(f"Код валюты должен быть в верхнем регистре: {code}")
        if " " in code:
            raise ValueError("Код валюты не должен содержать пробелы")
        
        #валидация имени
        if not name or not name.strip():
            raise ValueError("Имя валюты не может быть пустым")

        self.code = code
        self.name = name

    @abstractmethod
    def get_display_info(self) -> str:
        pass

    def __str__(self):
        return f"{self.code} ({self.name})"


class FiatCurrency(Currency):
    #фиатные деньги
    def __init__(self, code: str, name: str, issuing_country: str):
        super().__init__(code, name)
        self.issuing_country = issuing_country

    def get_display_info(self) -> str:
        return f"[FIAT] {self.code} — {self.name} (Issuing: {self.issuing_country})"


class CryptoCurrency(Currency):
    #крипта
    def __init__(self, code: str, name: str, algorithm: str, market_cap: float = 0.0):
        super().__init__(code, name)
        self.algorithm = algorithm
        self.market_cap = market_cap

    def get_display_info(self) -> str:
        return f"[CRYPTO] {self.code} — {self.name} (Algo: {self.algorithm}, MCAP: {self.market_cap:.2e})"


#реестр доступных валют git add .
git commit -m "архитектура: добавил классы валют и исключения"
_REGISTRY: Dict[str, Currency] = {
    "USD": FiatCurrency("USD", "US Dollar", "United States"),
    "EUR": FiatCurrency("EUR", "Euro", "Eurozone"),
    "RUB": FiatCurrency("RUB", "Russian Ruble", "Russia"),
    "BTC": CryptoCurrency("BTC", "Bitcoin", "SHA-256", 1.12e12),
    "ETH": CryptoCurrency("ETH", "Ethereum", "Ethash", 4.5e11),
    "USDT": CryptoCurrency("USDT", "Tether", "ERC-20", 8.3e10)
}

def get_currency(code: str) -> Currency:
    #фабричный метод получения валюты
    if code not in _REGISTRY:
        raise CurrencyNotFoundError(code)
    return _REGISTRY[code]