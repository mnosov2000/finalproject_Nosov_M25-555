import requests
from abc import ABC, abstractmethod
from typing import Dict, Any
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig

class BaseApiClient(ABC):
    def __init__(self, config: ParserConfig):
        self.config = config

    @abstractmethod
    def fetch_rates(self) -> Dict[str, float]:
        pass

class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self) -> Dict[str, float]:
        ids = ",".join(self.config.CRYPTO_ID_MAP.values())
        params = {
            "ids": ids,
            "vs_currencies": self.config.BASE_CURRENCY.lower()
        }

        try:
            resp = requests.get(
                self.config.COINGECKO_URL, 
                params=params, 
                timeout=self.config.REQUEST_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise ApiRequestError(f"CoinGecko error: {e}")

        result = {}
        # инвертируем мапу 
        id_to_code = {v: k for k, v in self.config.CRYPTO_ID_MAP.items()}

        for coin_id, prices in data.items():
            if coin_id in id_to_code:
                code = id_to_code[coin_id]
                rate = prices.get(self.config.BASE_CURRENCY.lower())
                if rate:
                    pair = f"{code}_{self.config.BASE_CURRENCY}"
                    result[pair] = float(rate)
        
        return result

class ExchangeRateApiClient(BaseApiClient):
    def fetch_rates(self) -> Dict[str, float]:
        if not self.config.EXCHANGERATE_API_KEY:
            raise ApiRequestError("ExchangeRate API key is missing")

        url = f"{self.config.EXCHANGERATE_API_URL}/{self.config.EXCHANGERATE_API_KEY}/latest/{self.config.BASE_CURRENCY}"

        try:
            resp = requests.get(url, timeout=self.config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            #print(f"DEBUG URL: {url}")
            #print(f"DEBUG DATA: {data}")

        except requests.RequestException as e:
            raise ApiRequestError(f"ExchangeRateAPI error: {e}")

        rates = data.get("conversion_rates", {})
        result = {}

        for code in self.config.FIAT_CURRENCIES:
            if code in rates:
                val = float(rates[code])
                if val > 0:
                    real_rate = 1.0 / val
                    pair = f"{code}_{self.config.BASE_CURRENCY}"
                    result[pair] = real_rate
        
        return result