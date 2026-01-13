import os
from typing import Any

class SettingsLoader:
    #синглтон настроек
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsLoader, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._settings = {
            "DATA_DIR": "data",
            "USERS_FILE": os.path.join("data", "users.json"),
            "PORTFOLIOS_FILE": os.path.join("data", "portfolios.json"),
            "RATES_FILE": os.path.join("data", "rates.json"),
            "RATES_TTL_SECONDS": 300,  
            "DEFAULT_BASE_CURRENCY": "USD",
            "LOG_FILE": "valutatrade.log",
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "%(asctime)s %(levelname)s %(message)s",
            "EXCHANGERATE_API_KEY": "b2e2c396d4c0fe08bb7f8d87" 
        }

    def get(self, key: str, default: Any = None) -> Any:
        return self._settings.get(key, default)

    def reload(self):
        self._initialize()