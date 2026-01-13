import os
from dataclasses import dataclass, field
from typing import Tuple, Dict
from valutatrade_hub.infra.settings import SettingsLoader

@dataclass
class ParserConfig:
     
    _settings = SettingsLoader()
    
    
    EXCHANGERATE_API_KEY: str = _settings.get("EXCHANGERATE_API_KEY")

    # ссылки
    COINGECKO_URL: str = "https://api.coingecko.com/api/v3/simple/price"
    EXCHANGERATE_API_URL: str = "https://v6.exchangerate-api.com/v6"

    # параметры
    BASE_CURRENCY: str = "USD"
    FIAT_CURRENCIES: Tuple[str, ...] = ("EUR", "GBP", "RUB", "CNY")
    CRYPTO_CURRENCIES: Tuple[str, ...] = ("BTC", "ETH", "SOL", "USDT")
    
    # маппинг
    CRYPTO_ID_MAP: Dict[str, str] = field(default_factory=lambda: {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "USDT": "tether"
    })

    # пути
    RATES_FILE_PATH: str = os.path.join("data", "rates.json")
    HISTORY_FILE_PATH: str = os.path.join("data", "exchange_rates.json")

    REQUEST_TIMEOUT: int = 10